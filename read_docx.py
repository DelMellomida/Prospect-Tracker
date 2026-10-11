try:
    import zipfile, xml.etree.ElementTree as ET
    docx_path = 'docs/Prospect Tracker - Design Doc 2.docx'
    z = zipfile.ZipFile(docx_path)
    xml_content = z.read('word/document.xml').decode('utf-8')
    root = ET.fromstring(xml_content)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    texts = []
    for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            texts.append(t.text)
    full_text = '\n'.join(texts)
    print(full_text[:12000])
except Exception as e:
    print('error:', e)
