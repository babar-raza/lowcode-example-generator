"""Assembly identity reading and deduplication for .NET dependency DLLs.

The core problem this module solves:
  Multiple NuGet packages can provide DLLs with the same assembly simple name
  (e.g. System.Memory.dll from System.Memory 4.5.3 and 4.5.5).  When
  DllReflector receives duplicate paths in --deps, PathAssemblyResolver tries
  to LoadFromAssemblyPath() the same identity twice, which throws
  FileLoadException: already loaded.

  Additionally, TRUSTED_PLATFORM_ASSEMBLIES (added by DllReflector at runtime)
  can provide the same assembly as a NuGet dep (e.g. System.Text.Json in
  net8.0 trusted assemblies AND in the NuGet resolved-libs).

This module handles the Python-side fix: deduplicate dep_dll_paths by
assembly identity (name) before they are passed to DllReflector, keeping
the first-seen path for each unique assembly simple name and recording
all excluded duplicates in a structured report.
"""

from __future__ import annotations

import struct
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Coded-index reference tables from ECMA-335 §24.2.6 ─────────────────────
# Each entry: list of table IDs that can be referenced (None = unused tag slot),
# and the number of bits used for the tag.
_CODED_INDEX_DEFS: dict[str, tuple[list[int | None], int]] = {
    "TypeDefOrRef":      ([0x02, 0x01, 0x1B], 2),
    "HasConstant":       ([0x04, 0x08, 0x17], 2),
    "HasCustomAttribute": (
        [0x06, 0x04, 0x01, 0x02, 0x08, 0x0A, 0x0C,
         0x14, 0x17, 0x0E, 0x15, 0x12, 0x1C, 0x11,
         0x00, 0x20, 0x21, 0x22, 0x23, 0x26, 0x27,
         0x28, 0x2A, 0x2B, 0x2C], 5),
    "HasFieldMarshal":   ([0x04, 0x08], 1),
    "HasDeclSecurity":   ([0x02, 0x06, 0x20], 2),
    "MemberRefParent":   ([0x02, 0x01, 0x1A, 0x06, 0x1B], 3),
    "HasSemantics":      ([0x14, 0x17], 1),
    "MethodDefOrRef":    ([0x06, 0x0A], 1),
    "MemberForwarded":   ([0x04, 0x06], 1),
    "Implementation":    ([0x26, 0x23, 0x27], 2),
    "CustomAttributeType": ([None, None, 0x06, 0x0A, None], 3),
    "ResolutionScope":   ([0x00, 0x1A, 0x23, 0x01], 2),
    "TypeOrMethodDef":   ([0x02, 0x06], 1),
}

# Table schemas: table_id → list of column descriptors.
# Each descriptor is one of:
#   ('fixed', N)       — fixed N-byte integer
#   ('str',)           — string heap index
#   ('blob',)          — blob heap index
#   ('guid',)          — GUID heap index
#   ('table', T)       — simple index into table T
#   ('coded', name)    — coded index named 'name' (see _CODED_INDEX_DEFS)
_TABLE_SCHEMAS: dict[int, list] = {
    0x00: [('fixed', 2), ('str',), ('guid',), ('guid',), ('guid',)],
    0x01: [('coded', 'ResolutionScope'), ('str',), ('str',)],
    0x02: [('fixed', 4), ('str',), ('str',), ('coded', 'TypeDefOrRef'),
           ('table', 0x04), ('table', 0x06)],
    0x03: [('table', 0x04)],
    0x04: [('fixed', 2), ('str',), ('blob',)],
    0x05: [('table', 0x06)],
    0x06: [('fixed', 4), ('fixed', 2), ('fixed', 2), ('str',), ('blob',),
           ('table', 0x08)],
    0x07: [('table', 0x08)],
    0x08: [('fixed', 2), ('fixed', 2), ('str',)],
    0x09: [('table', 0x02), ('coded', 'TypeDefOrRef')],
    0x0A: [('coded', 'MemberRefParent'), ('str',), ('blob',)],
    0x0B: [('fixed', 1), ('fixed', 1), ('coded', 'HasConstant'), ('blob',)],
    0x0C: [('coded', 'HasCustomAttribute'), ('coded', 'CustomAttributeType'),
           ('blob',)],
    0x0D: [('coded', 'HasFieldMarshal'), ('blob',)],
    0x0E: [('fixed', 2), ('coded', 'HasDeclSecurity'), ('blob',)],
    0x0F: [('fixed', 2), ('fixed', 4), ('table', 0x02)],
    0x10: [('fixed', 4), ('table', 0x04)],
    0x11: [('blob',)],
    0x12: [('table', 0x02), ('table', 0x14)],
    0x13: [('table', 0x14)],
    0x14: [('fixed', 2), ('str',), ('coded', 'TypeDefOrRef')],
    0x15: [('table', 0x02), ('table', 0x17)],
    0x16: [('table', 0x17)],
    0x17: [('fixed', 2), ('str',), ('blob',)],
    0x18: [('fixed', 2), ('table', 0x06), ('coded', 'HasSemantics')],
    0x19: [('table', 0x02), ('coded', 'MethodDefOrRef'),
           ('coded', 'MethodDefOrRef')],
    0x1A: [('str',)],
    0x1B: [('blob',)],
    0x1C: [('fixed', 2), ('coded', 'MemberForwarded'), ('str',),
           ('table', 0x1A)],
    0x1D: [('fixed', 4), ('table', 0x04)],
    # Assembly table (target of this parser)
    0x20: [('fixed', 4),          # HashAlgId
           ('fixed', 2),          # MajorVersion
           ('fixed', 2),          # MinorVersion
           ('fixed', 2),          # BuildNumber
           ('fixed', 2),          # RevisionNumber
           ('fixed', 4),          # Flags
           ('blob',),             # PublicKey
           ('str',),              # Name
           ('str',)],             # Culture
}


@dataclass
class AssemblyIdentity:
    """Identity of a .NET assembly."""
    name: str
    version: str = ""
    culture: str = "neutral"
    public_key_token: str = ""
    source_path: str = ""
    read_from_pe: bool = False


@dataclass
class DeduplicationResult:
    """Result of deduplicating a list of assembly paths."""
    kept: list[Path] = field(default_factory=list)
    excluded: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    dedup_by: str = "assembly_simple_name"


def read_assembly_identity(path: Path | str) -> AssemblyIdentity:
    """Read assembly identity (name, version) from a .NET PE file.

    Parses the PE/CLI metadata to extract the Assembly table row.
    Falls back to filename-based identity if parsing fails.

    Args:
        path: Path to a .NET DLL file.

    Returns:
        AssemblyIdentity with name, version, and source_path populated.
    """
    path = Path(path)
    try:
        with open(path, "rb") as f:
            data = f.read()
        identity = _parse_cli_assembly_identity(data, str(path))
        identity.read_from_pe = True
        return identity
    except Exception as exc:
        logger.debug(
            "PE parse failed for %s (%s), falling back to filename", path.name, exc
        )
        return AssemblyIdentity(name=path.stem, source_path=str(path))


def deduplicate_assemblies(
    paths: list[Path],
    preference_rules: dict | None = None,
) -> DeduplicationResult:
    """Deduplicate assembly paths by assembly simple name.

    For each unique assembly simple name, keeps the first path encountered.
    Excluded duplicates are recorded with their reason.

    Deduplication is by assembly simple name (case-insensitive), not by full
    identity. This ensures PathAssemblyResolver never receives two paths
    that map to the same assembly name, which would cause FileLoadException.

    Args:
        paths: List of DLL paths (may contain duplicates).
        preference_rules: Reserved for future use (e.g. prefer specific TFM).

    Returns:
        DeduplicationResult with kept paths, excluded duplicates, and conflicts.
    """
    result = DeduplicationResult()
    seen: dict[str, Path] = {}  # lower assembly name → first path

    for p in paths:
        identity = read_assembly_identity(p)
        key = identity.name.lower()

        if key not in seen:
            seen[key] = p
            result.kept.append(p)
        else:
            first = seen[key]
            conflict_note = None
            if first.resolve() != p.resolve():
                # Different files with same assembly name — possible version conflict
                conflict_note = {
                    "assembly_name": identity.name,
                    "kept_path": str(first),
                    "excluded_path": str(p),
                    "note": "same-name assemblies from different files; first-seen path kept",
                }
                result.conflicts.append(conflict_note)

            result.excluded.append({
                "assembly_name": identity.name,
                "excluded_path": str(p),
                "kept_path": str(first),
                "same_file": first.resolve() == p.resolve(),
                "reason": "duplicate_assembly_name",
            })
            logger.debug(
                "Excluded duplicate assembly '%s': %s (kept: %s)",
                identity.name, p.name, first.name,
            )

    return result


# ── PE parser internals ──────────────────────────────────────────────────────

def _parse_cli_assembly_identity(data: bytes, path: str) -> AssemblyIdentity:
    """Parse a .NET PE file and return the Assembly table identity."""
    if len(data) < 128 or data[:2] != b"MZ":
        raise ValueError("Not a valid PE file")

    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off : pe_off + 4] != b"PE\x00\x00":
        raise ValueError("Missing PE signature")

    # COFF header
    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]

    # Optional header
    opt_off = pe_off + 24
    magic = struct.unpack_from("<H", data, opt_off)[0]
    if magic == 0x10B:      # PE32
        dd_off = opt_off + 96
    elif magic == 0x20B:    # PE32+
        dd_off = opt_off + 112
    else:
        raise ValueError(f"Unknown PE magic: {magic:#x}")

    # Data directory 14 = CLI descriptor
    cli_rva = struct.unpack_from("<I", data, dd_off + 14 * 8)[0]
    if cli_rva == 0:
        raise ValueError("No CLI header (not a .NET assembly)")

    # Section table
    sections_off = opt_off + opt_size
    sections = [
        struct.unpack_from("<2I4H2I", data, sections_off + i * 40)  # name is first 8 bytes
        for i in range(num_sections)
    ]
    raw_sections = []
    for i in range(num_sections):
        s = sections_off + i * 40
        virt_size = struct.unpack_from("<I", data, s + 8)[0]
        virt_addr = struct.unpack_from("<I", data, s + 12)[0]
        raw_size  = struct.unpack_from("<I", data, s + 16)[0]
        raw_off   = struct.unpack_from("<I", data, s + 20)[0]
        raw_sections.append((virt_addr, max(virt_size, raw_size), raw_off))

    def rva_to_off(rva: int) -> int:
        for virt_addr, span, raw_off in raw_sections:
            if virt_addr <= rva < virt_addr + span:
                return raw_off + (rva - virt_addr)
        raise ValueError(f"RVA {rva:#x} not in any section")

    # CLI header: bytes 8-11 = MetaData RVA
    cli_off = rva_to_off(cli_rva)
    md_rva = struct.unpack_from("<I", data, cli_off + 8)[0]
    md_off = rva_to_off(md_rva)

    # Metadata root magic "BSJB"
    if struct.unpack_from("<I", data, md_off)[0] != 0x424A5342:
        raise ValueError("Invalid .NET metadata root signature")

    # Version string length (padded to 4 bytes)
    ver_str_len = struct.unpack_from("<I", data, md_off + 12)[0]
    # Flags(2) + NumberOfStreams(2) at md_off + 16 + ver_str_len
    flags_off = md_off + 16 + ver_str_len
    num_streams = struct.unpack_from("<H", data, flags_off + 2)[0]

    # Parse stream headers
    sh_off = flags_off + 4
    stream_map: dict[str, tuple[int, int]] = {}
    for _ in range(num_streams):
        rel_off = struct.unpack_from("<I", data, sh_off)[0]
        size    = struct.unpack_from("<I", data, sh_off + 4)[0]
        name_start = sh_off + 8
        null_idx = data.index(b"\x00", name_start)
        sname = data[name_start:null_idx].decode("ascii")
        # Pad name to next 4-byte boundary
        name_bytes = null_idx - name_start + 1
        padded = ((name_bytes + 3) // 4) * 4
        sh_off = name_start + padded
        stream_map[sname] = (md_off + rel_off, size)

    if "#~" not in stream_map or "#Strings" not in stream_map:
        raise ValueError("Missing #~ or #Strings stream in metadata")

    tables_off = stream_map["#~"][0]
    strings_off = stream_map["#Strings"][0]

    # #~ stream header
    heap_sizes = data[tables_off + 6]
    valid_mask = struct.unpack_from("<Q", data, tables_off + 8)[0]

    str_idx  = 4 if (heap_sizes & 0x01) else 2
    guid_idx = 4 if (heap_sizes & 0x02) else 2
    blob_idx = 4 if (heap_sizes & 0x04) else 2

    # Row counts for each present table (4 bytes each)
    rc_off = tables_off + 24  # after Reserved(4)+MajorVer(1)+MinorVer(1)+HeapSizes(1)+Res(1)+Valid(8)+Sorted(8)
    row_counts: dict[int, int] = {}
    for t in range(64):
        if valid_mask & (1 << t):
            row_counts[t] = struct.unpack_from("<I", data, rc_off)[0]
            rc_off += 4

    # Row data starts after row counts
    rows_data_off = rc_off

    # Helper: compute index size for a simple table reference
    def table_idx(t: int) -> int:
        return 4 if row_counts.get(t, 0) > 0xFFFF else 2

    # Helper: compute coded index size
    def coded_idx(name: str) -> int:
        refs, n_bits = _CODED_INDEX_DEFS[name]
        threshold = 1 << (16 - n_bits)
        for t in refs:
            if t is not None and row_counts.get(t, 0) >= threshold:
                return 4
        return 2

    # Helper: compute row size for a table
    def row_size(t: int) -> int:
        schema = _TABLE_SCHEMAS.get(t)
        if schema is None:
            return 0
        size = 0
        for col in schema:
            kind = col[0]
            if kind == "fixed":
                size += col[1]
            elif kind == "str":
                size += str_idx
            elif kind == "blob":
                size += blob_idx
            elif kind == "guid":
                size += guid_idx
            elif kind == "table":
                size += table_idx(col[1])
            elif kind == "coded":
                size += coded_idx(col[1])
        return size

    # Navigate to Assembly table (0x20)
    # Sum row sizes for all tables 0x00..0x1F that are present
    off = rows_data_off
    for t in range(0x20):
        rc = row_counts.get(t, 0)
        if rc > 0:
            rs = row_size(t)
            off += rc * rs

    # Read first Assembly row
    # Columns: HashAlgId(4) + MajorVer(2) + MinorVer(2) + Build(2) + Rev(2)
    #          + Flags(4) + PublicKey(blob_idx) + Name(str_idx) + Culture(str_idx)
    if row_counts.get(0x20, 0) == 0:
        raise ValueError("No Assembly table in metadata")

    hash_alg = struct.unpack_from("<I", data, off)[0]; off += 4
    major    = struct.unpack_from("<H", data, off)[0];  off += 2
    minor    = struct.unpack_from("<H", data, off)[0];  off += 2
    build    = struct.unpack_from("<H", data, off)[0];  off += 2
    rev      = struct.unpack_from("<H", data, off)[0];  off += 2
    flags    = struct.unpack_from("<I", data, off)[0];  off += 4
    off += blob_idx  # skip PublicKey blob index

    if str_idx == 2:
        name_si = struct.unpack_from("<H", data, off)[0]; off += 2
        culture_si = struct.unpack_from("<H", data, off)[0]
    else:
        name_si = struct.unpack_from("<I", data, off)[0]; off += 4
        culture_si = struct.unpack_from("<I", data, off)[0]

    # Read name from #Strings heap
    name_raw_off = strings_off + name_si
    null_idx = data.index(b"\x00", name_raw_off)
    asm_name = data[name_raw_off:null_idx].decode("utf-8", errors="replace")

    # Read culture
    culture_raw_off = strings_off + culture_si
    null_idx2 = data.index(b"\x00", culture_raw_off)
    culture = data[culture_raw_off:null_idx2].decode("utf-8", errors="replace") or "neutral"

    version_str = f"{major}.{minor}.{build}.{rev}"

    return AssemblyIdentity(
        name=asm_name,
        version=version_str,
        culture=culture,
        source_path=path,
    )
