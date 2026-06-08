# Central Package Management Decision

All 3 plugin repos adopt `ManagePackageVersionsCentrally=true` via `Directory.Packages.props`.
Per-example csproj files omit explicit Version attributes.
This matches LowCode example repo convention exactly.
