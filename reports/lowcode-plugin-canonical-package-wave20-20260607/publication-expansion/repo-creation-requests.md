# Target Repo Creation Requests

The following GitHub repos need to be created to publish remaining PCLC packages.
Format: `aspose-{family}-net/Aspose.{Product}.Plugins-for-.NET-Examples`

| Family | Repo | Packages |
|--------|------|---------|
| HTML | aspose-html-net/Aspose.HTML.Plugins-for-.NET-Examples | convert-html-to-markdown, merge-html, convert-html-to-xps |
| PDF (plugin) | aspose-pdf-net/Aspose.PDF.Plugins-for-.NET-Examples | (separate from legacy pdf#22) |
| GIS | aspose-gis-net/Aspose.GIS.Plugins-for-.NET-Examples | read-gis-data, convert-gis-data |
| TeX | aspose-tex-net/Aspose.TeX.Plugins-for-.NET-Examples | convert-latex-to-pdf |
| PSD | aspose-psd-net/Aspose.PSD.Plugins-for-.NET-Examples | convert-psd-to-png |
| Tasks | aspose-tasks-net/Aspose.Tasks.Plugins-for-.NET-Examples | read-project-data |
| Font | aspose-font-net/Aspose.Font.Plugins-for-.NET-Examples | convert-font, render-text-with-font |
| 3D | aspose-3d-net/Aspose.3D.Plugins-for-.NET-Examples | convert-3d-model, compress-3d-scene |
| OMR | aspose-omr-net/Aspose.OMR.Plugins-for-.NET-Examples | generate-omr-template, recognize-omr |
| Finance | aspose-finance-net/Aspose.Finance.Plugins-for-.NET-Examples | parse-xbrl |

**Action Required:** Human reviewer to create each repo and update pipeline/configs/families/*.yml with the new repo names.
