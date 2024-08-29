export function sanitizeFileName(input: string, maxLength = 100): string {
    const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g;
    const reservedNames = /^(CON|PRN|AUX|NUL|COM\d|LPT\d)(\..*)?$/i;
    let sanitized = input
      .replace(invalidChars, "_")
      .replace(/ /g, "_")
      .replace(/[. ]+$/, "");
    if (reservedNames.test(sanitized)) {
      sanitized = sanitized.replace(reservedNames, "_$1");
    }
    if (sanitized.length > maxLength) {
      const extensionMatch = sanitized.match(/(\.[^.]+)$/);
      const extension = extensionMatch ? extensionMatch[0] : "";
      const baseLength = maxLength - extension.length;
      sanitized = sanitized.slice(0, baseLength) + extension;
    }
    return sanitized;
  }
  