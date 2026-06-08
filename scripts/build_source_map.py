"""Build plugin-to-source-code map for all families from GitHub repo trees."""
import json, re, hashlib, time
from pathlib import Path

# Map plugin slug to search keywords in file paths
PLUGIN_KEYWORDS = {
    'barcode': {
        'generate-barcode': ['BarcodeOutput', 'StoreBarcode', 'Generate'],
        'recognize-barcode': ['Recognition', 'ReadSimple', 'Recognize'],
        'generate-qr-code': ['QR', 'QrCode', 'QRCode'],
        'read-barcode': ['Recognition', 'ReadBase', 'ReadMain'],
        'scan-barcode': ['Scan', 'Recognition'],
    },
    'imaging': {
        'convert-image': ['ConvertImage', 'ExportTo', 'SavingOptions'],
        'resize-image': ['Resize'],
        'compress-image': ['Compress'],
        'crop-image': ['Crop'],
        'rotate-image': ['Rotate', 'Flip'],
        'watermark-image': ['Watermark', 'TextWatermark'],
        'merge-images': ['Merge', 'Combine'],
        'filter-image': ['Filter'],
    },
    'zip': {
        'compress-files': ['AddEntry', 'Compress', 'CreateArchive'],
        'extract-files': ['ExtractAll', 'ExtractEntry'],
        'create-archive': ['CreateArchive', 'Archive'],
        'compress-folder': ['Folder', 'Directory'],
    },
    'html': {
        'convert-html-to-pdf': ['HtmlToPdf', 'ConvertHTML', 'Pdf'],
        'convert-html-to-word': ['HtmlToDoc', 'Word'],
        'convert-html-to-image': ['HtmlToImage', 'Image'],
        'convert-html-to-xps': ['HtmlToXps', 'Xps'],
        'convert-html-to-markdown': ['Markdown'],
        'merge-html': ['MergeHTML', 'Merge'],
    },
    'tasks': {
        'convert-mpp-to-pdf': ['SavePdf', 'ToPdf', 'Pdf'],
        'convert-mpp-to-excel': ['Excel', 'Xlsx', 'ToExcel'],
        'convert-mpp-to-html': ['HTML', 'ToHtml'],
        'convert-mpp-to-image': ['Image', 'Png', 'ToImage'],
        'read-project-data': ['ReadProject', 'LoadProject', 'ReadTask'],
    },
    'cad': {
        'convert-cad-to-pdf': ['ToPdf', 'SavePdf', 'PdfOptions'],
        'convert-dwg-to-pdf': ['DwgToPdf', 'Dwg'],
        'convert-dxf-to-pdf': ['DxfToPdf', 'Dxf'],
        'convert-cad-to-image': ['ToImage', 'CadToImage', 'BmpOptions', 'JpegOptions'],
        'convert-dwg-to-jpg': ['DwgToJpg', 'DwgToJpeg'],
    },
    'ocr': {
        'recognize-text': ['RecognizePage', 'RecognizeImage', 'Recognize'],
        'extract-text': ['ExtractText', 'GetText'],
        'scan-document': ['ScanDocument', 'Document'],
    },
    'psd': {
        'convert-psd-to-pdf': ['PsdToPdf', 'Pdf'],
        'convert-psd-to-png': ['PsdToPng', 'Png'],
        'convert-psd-to-jpg': ['PsdToJpg', 'Jpeg'],
        'edit-psd-layers': ['Layer', 'EditLayer'],
    },
    'svg': {
        'convert-svg-to-pdf': ['SvgToPdf', 'Pdf'],
        'convert-svg-to-png': ['SvgToPng', 'Png'],
        'convert-svg-to-jpg': ['SvgToJpg', 'Jpg'],
        'merge-svg': ['MergeSvg', 'Merge'],
    },
    'page': {
        'convert-xps-to-pdf': ['XpsToPdf', 'Xps'],
        'convert-eps-to-pdf': ['EpsToPdf', 'Eps'],
        'convert-ps-to-pdf': ['PsToPdf', 'Ps'],
    },
    'tex': {
        'convert-tex-to-pdf': ['TexToPdf', 'Pdf'],
        'convert-latex-to-pdf': ['LatexToPdf', 'Latex'],
        'convert-tex-to-svg': ['TexToSvg', 'Svg'],
    },
    'note': {
        'convert-one-to-pdf': ['OneToPdf', 'ToPdf', 'Pdf'],
        'convert-one-to-word': ['OneToWord', 'ToDoc', 'Word'],
        'convert-one-to-image': ['OneToImage', 'ToImage', 'Image'],
    },
    'drawing': {
        'convert-drawing': ['ConvertDrawing', 'Convert', 'Save'],
        'create-drawing': ['CreateDrawing', 'Create', 'Draw'],
    },
    'font': {
        'convert-font': ['ConvertFont', 'Font', 'Save'],
        'render-text-with-font': ['RenderText', 'Render'],
    },
    'finance': {
        'convert-xbrl': ['ConvertXbrl', 'Xbrl', 'Convert'],
        'parse-xbrl': ['ParseXbrl', 'Parse'],
    },
    'threed': {
        'convert-3d-model': ['Convert', 'Scene', 'Save'],
        'compress-3d-scene': ['Compress', 'Scene'],
    },
    'gis': {
        'convert-gis-data': ['ConvertLayer', 'Convert', 'Layer'],
        'read-gis-data': ['ReadLayer', 'ReadFeature', 'Read'],
    },
    'omr': {
        'recognize-omr': ['RecognizeOmr', 'Recognize'],
        'generate-omr-template': ['GenerateTemplate', 'Template'],
    },
}

FAMILY_REPOS = {
    'barcode': 'aspose-barcode/Aspose.BarCode-for-.NET',
    'imaging': 'aspose-imaging/Aspose.Imaging-for-.NET',
    'zip': 'aspose-zip/Aspose.ZIP-for-.NET',
    'html': 'aspose-html/Aspose.HTML-for-.NET',
    'tasks': 'aspose-tasks/Aspose.Tasks-for-.NET',
    'cad': 'aspose-cad/Aspose.CAD-for-.NET',
    'ocr': 'aspose-ocr/Aspose.OCR-for-.NET',
    'psd': 'aspose-psd/Aspose.PSD-for-.NET',
    'svg': 'aspose-svg/Aspose.SVG-for-.NET',
    'page': 'aspose-page/Aspose.Page-for-.NET',
    'tex': 'aspose-tex/Aspose.TeX-for-.NET',
    'note': 'aspose-note/Aspose.Note-for-.NET',
    'drawing': 'aspose-drawing/Aspose.Drawing-for-.NET',
    'font': 'aspose-font/Aspose.Font-for-.NET',
    'finance': 'aspose-finance/Aspose.Finance-for-.NET',
    'threed': 'aspose-3d/Aspose.3D-for-.NET',
    'gis': 'aspose-gis/Aspose.GIS-for-.NET',
    'omr': 'aspose-omr/Aspose.OMR-for-.NET',
}

SKIP_PATTERNS = ['DEMO', 'LIVE', 'UI', 'WEBAPP', 'APP_START', 'CONTROLLERS', 'MODELS', 'MIGRATION', 'PROPERTIES/ASSEMBLYINFO']

tree_cache = Path('.local/code-cache/repo-trees')
code_cache = Path('.local/code-cache')
source_map = {}

for family in sorted(FAMILY_REPOS.keys()):
    tree_file = tree_cache / f'{family}-tree.json'
    if not tree_file.exists():
        print(f'No tree for {family}')
        continue

    with open(tree_file) as f:
        data = json.load(f)

    tree = data.get('tree', [])
    cs_files = [x['path'] for x in tree if x.get('path', '').endswith('.cs')]

    plugins = PLUGIN_KEYWORDS.get(family, {})
    source_map[family] = {}

    for plugin, keywords in plugins.items():
        matches = []
        for cs_path in cs_files:
            path_upper = cs_path.upper()
            if any(skip in path_upper for skip in SKIP_PATTERNS):
                continue
            if any(kw.upper() in path_upper for kw in keywords):
                matches.append(cs_path)
        # Prefer shorter paths (top-level examples are simpler)
        matches.sort(key=lambda p: (len(p.split('/')), p))
        source_map[family][plugin] = matches[:3]

    plugin_count = len([p for p, m in source_map[family].items() if m])
    print(f'{family}: {plugin_count}/{len(plugins)} plugins matched, {len(cs_files)} C# files total')

output = code_cache / 'plugin-source-map.json'
output.write_text(json.dumps(source_map, indent=2))
print(f'Saved to {output}')
