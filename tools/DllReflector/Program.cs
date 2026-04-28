// DllReflector — Metadata-only reflection tool
//
// SAFETY INVARIANTS:
// 1. Uses MetadataLoadContext exclusively — no code execution.
// 2. Never calls Activator.CreateInstance, MethodInfo.Invoke, or ConstructorInfo.Invoke.
// 3. Never triggers static constructors.
// 4. No Aspose package references — DLL path supplied via CLI.
// 5. Assembly is loaded for metadata inspection only.

using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Xml.Linq;

var dllPath = "";
var xmlPath = "";
var outputPath = "";
var depPaths = new List<string>();

for (int i = 0; i < args.Length; i++)
{
    switch (args[i])
    {
        case "--dll":
            dllPath = args[++i];
            break;
        case "--xml":
            xmlPath = args[++i];
            break;
        case "--output":
            outputPath = args[++i];
            break;
        case "--deps":
            // Remaining args are dep paths until next flag or end
            while (i + 1 < args.Length && !args[i + 1].StartsWith("--"))
            {
                depPaths.Add(args[++i]);
            }
            break;
    }
}

if (string.IsNullOrEmpty(dllPath))
{
    Console.Error.WriteLine("Error: --dll <path> is required");
    return 1;
}

if (string.IsNullOrEmpty(outputPath))
{
    Console.Error.WriteLine("Error: --output <path> is required");
    return 1;
}

if (!File.Exists(dllPath))
{
    Console.Error.WriteLine($"Error: DLL not found: {dllPath}");
    return 2;
}

// Build the list of assembly paths for the resolver
var resolverPaths = new List<string> { dllPath };
resolverPaths.AddRange(depPaths.Where(File.Exists));

// Add trusted platform assemblies (runtime reference assemblies)
var trustedAssemblies = (AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES") as string ?? "")
    .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries);
resolverPaths.AddRange(trustedAssemblies);

// Load XML documentation if available
Dictionary<string, string>? xmlDocs = null;
var xmlWarning = (string?)null;
if (!string.IsNullOrEmpty(xmlPath) && File.Exists(xmlPath))
{
    xmlDocs = ParseXmlDocs(xmlPath);
}
else
{
    xmlWarning = string.IsNullOrEmpty(xmlPath)
        ? "No XML documentation path provided"
        : $"XML documentation file not found: {xmlPath}";
}

// METADATA-ONLY: Use MetadataLoadContext — no code execution
var resolver = new PathAssemblyResolver(resolverPaths);
using var mlc = new MetadataLoadContext(resolver);

Assembly assembly;
try
{
    assembly = mlc.LoadFromAssemblyPath(Path.GetFullPath(dllPath));
}
catch (Exception ex)
{
    Console.Error.WriteLine($"Error: Failed to load assembly: {ex.Message}");
    return 3;
}

var assemblyName = assembly.GetName();
var result = new Dictionary<string, object?>
{
    ["assembly_name"] = assemblyName.Name,
    ["assembly_version"] = assemblyName.Version?.ToString(),
    ["target_framework"] = GetTargetFramework(assembly),
    ["namespaces"] = new List<object>(),
    ["diagnostics"] = new Dictionary<string, object?>
    {
        ["xml_documentation_loaded"] = xmlDocs != null,
        ["xml_warning"] = xmlWarning,
        ["dependency_paths_provided"] = depPaths.Count,
        ["metadata_only"] = true,
    }
};

// Enumerate public types grouped by namespace
var publicTypes = new List<Type>();
try
{
    publicTypes = assembly.GetTypes().Where(t => t.IsPublic).ToList();
}
catch (ReflectionTypeLoadException ex)
{
    publicTypes = ex.Types.Where(t => t != null && t.IsPublic).ToList()!;
    ((Dictionary<string, object?>)result["diagnostics"]!)["type_load_errors"] =
        ex.LoaderExceptions.Select(e => e?.Message).Where(m => m != null).Distinct().ToList();
}

var namespaceGroups = publicTypes
    .GroupBy(t => t.Namespace ?? "(global)")
    .OrderBy(g => g.Key);

var namespaceList = new List<object>();

foreach (var nsGroup in namespaceGroups)
{
    var types = new List<object>();

    foreach (var type in nsGroup.OrderBy(t => t.Name))
    {
        var typeInfo = BuildTypeInfo(type, xmlDocs);
        types.Add(typeInfo);
    }

    namespaceList.Add(new Dictionary<string, object>
    {
        ["namespace"] = nsGroup.Key,
        ["types"] = types,
    });
}

result["namespaces"] = namespaceList;

// Write output
var outputDir = Path.GetDirectoryName(Path.GetFullPath(outputPath));
if (!string.IsNullOrEmpty(outputDir))
    Directory.CreateDirectory(outputDir);

var json = JsonSerializer.Serialize(result, new JsonSerializerOptions
{
    WriteIndented = true,
    DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,
});

File.WriteAllText(outputPath, json);
Console.WriteLine($"Reflection catalog written to: {outputPath}");
return 0;

// --- Helper methods ---

static Dictionary<string, object> BuildTypeInfo(Type type, Dictionary<string, string>? xmlDocs)
{
    var info = new Dictionary<string, object>
    {
        ["name"] = type.Name,
        ["full_name"] = type.FullName ?? type.Name,
        ["kind"] = GetTypeKind(type),
        ["is_obsolete"] = HasObsolete(type),
    };

    var docKey = $"T:{type.FullName}";
    if (xmlDocs != null && xmlDocs.TryGetValue(docKey, out var summary))
        info["xml_summary"] = summary;

    if (type.IsEnum)
    {
        info["enum_values"] = GetEnumValues(type);
    }
    else
    {
        info["constructors"] = GetConstructors(type, xmlDocs);
        info["methods"] = GetMethods(type, xmlDocs);
        info["properties"] = GetProperties(type, xmlDocs);
    }

    return info;
}

static string GetTypeKind(Type type)
{
    if (type.IsEnum) return "enum";
    if (type.IsInterface) return "interface";
    if (type.IsValueType) return "struct";
    if (type.IsAbstract && type.IsSealed) return "static_class";
    if (type.IsAbstract) return "abstract_class";
    return "class";
}

static bool HasObsolete(MemberInfo member)
{
    return member.CustomAttributes.Any(a =>
        a.AttributeType.FullName == "System.ObsoleteAttribute");
}

static List<object> GetEnumValues(Type type)
{
    var values = new List<object>();
    foreach (var field in type.GetFields(BindingFlags.Public | BindingFlags.Static))
    {
        values.Add(new Dictionary<string, object>
        {
            ["name"] = field.Name,
            ["is_obsolete"] = HasObsolete(field),
        });
    }
    return values;
}

static List<object> GetConstructors(Type type, Dictionary<string, string>? xmlDocs)
{
    var ctors = new List<object>();
    foreach (var ctor in type.GetConstructors(BindingFlags.Public | BindingFlags.Instance))
    {
        var ctorInfo = new Dictionary<string, object>
        {
            ["parameters"] = GetParameters(ctor.GetParameters()),
            ["is_obsolete"] = HasObsolete(ctor),
        };

        var docKey = $"M:{type.FullName}.#ctor{GetParamDocSuffix(ctor.GetParameters())}";
        if (xmlDocs != null && xmlDocs.TryGetValue(docKey, out var summary))
            ctorInfo["xml_summary"] = summary;

        ctors.Add(ctorInfo);
    }
    return ctors;
}

static List<object> GetMethods(Type type, Dictionary<string, string>? xmlDocs)
{
    var methods = new List<object>();
    foreach (var method in type.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly)
        .Where(m => !m.IsSpecialName)
        .OrderBy(m => m.Name))
    {
        var methodInfo = new Dictionary<string, object>
        {
            ["name"] = method.Name,
            ["return_type"] = FormatTypeName(method.ReturnType),
            ["is_static"] = method.IsStatic,
            ["is_obsolete"] = HasObsolete(method),
            ["parameters"] = GetParameters(method.GetParameters()),
        };

        var docKey = $"M:{type.FullName}.{method.Name}{GetParamDocSuffix(method.GetParameters())}";
        if (xmlDocs != null && xmlDocs.TryGetValue(docKey, out var summary))
            methodInfo["xml_summary"] = summary;

        methods.Add(methodInfo);
    }
    return methods;
}

static List<object> GetProperties(Type type, Dictionary<string, string>? xmlDocs)
{
    var props = new List<object>();
    foreach (var prop in type.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly)
        .OrderBy(p => p.Name))
    {
        var propInfo = new Dictionary<string, object>
        {
            ["name"] = prop.Name,
            ["type"] = FormatTypeName(prop.PropertyType),
            ["can_read"] = prop.CanRead,
            ["can_write"] = prop.CanWrite,
            ["is_obsolete"] = HasObsolete(prop),
        };

        var docKey = $"P:{type.FullName}.{prop.Name}";
        if (xmlDocs != null && xmlDocs.TryGetValue(docKey, out var summary))
            propInfo["xml_summary"] = summary;

        props.Add(propInfo);
    }
    return props;
}

static List<object> GetParameters(ParameterInfo[] parameters)
{
    return parameters.Select(p => (object)new Dictionary<string, object>
    {
        ["name"] = p.Name ?? "",
        ["type"] = FormatTypeName(p.ParameterType),
        ["is_optional"] = p.IsOptional,
    }).ToList();
}

static string FormatTypeName(Type type)
{
    if (type.IsGenericType)
    {
        var name = type.Name;
        var backtick = name.IndexOf('`');
        if (backtick > 0)
            name = name[..backtick];
        var args = string.Join(", ", type.GetGenericArguments().Select(FormatTypeName));
        return $"{name}<{args}>";
    }
    return type.FullName ?? type.Name;
}

static string GetParamDocSuffix(ParameterInfo[] parameters)
{
    if (parameters.Length == 0)
        return "";
    var types = string.Join(",", parameters.Select(p => p.ParameterType.FullName ?? p.ParameterType.Name));
    return $"({types})";
}

static string? GetTargetFramework(Assembly assembly)
{
    var attr = assembly.CustomAttributes
        .FirstOrDefault(a => a.AttributeType.FullName == "System.Runtime.Versioning.TargetFrameworkAttribute");
    return attr?.ConstructorArguments.FirstOrDefault().Value?.ToString();
}

static Dictionary<string, string> ParseXmlDocs(string xmlPath)
{
    var docs = new Dictionary<string, string>();
    try
    {
        var doc = XDocument.Load(xmlPath);
        var members = doc.Descendants("member");
        foreach (var member in members)
        {
            var name = member.Attribute("name")?.Value;
            var summary = member.Element("summary")?.Value?.Trim();
            if (!string.IsNullOrEmpty(name) && !string.IsNullOrEmpty(summary))
            {
                docs[name] = summary;
            }
        }
    }
    catch (Exception ex)
    {
        Console.Error.WriteLine($"Warning: Failed to parse XML docs: {ex.Message}");
    }
    return docs;
}
