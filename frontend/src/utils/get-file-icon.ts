export const getIcon = (filename: string) => {
    // strip extension
    let extension = null;
    try {
      extension = filename.split('.').pop();
    } catch (e) {
      return 'tabler:file-unknown'
    }
    switch (extension) {
      case 'pdf':
        return 'tabler:file-type-pdf';
      case 'docx':
        return 'tabler:file-type-docx';
      case 'doc':
        return 'tabler:file-type-doc';
      case 'csv':
        return 'tabler:file-type-csv';
      case 'xls':
        return 'tabler:file-type-xls';
      case 'xlsx':
        return 'tabler:file-spreadsheet';
      case 'txt':
        return 'tabler:file-txt';
      case 'md':
        return 'tabler:file-text';
      case 'rtf':
        return 'tabler:file-text';
      case 'ppt':
        return 'tabler:file-type-ppt';
      case 'pptx':
        return 'tabler:file-chart';
      default:
        
    }
  }