from playwright.async_api import async_playwright

async def validate_mermaid_diagram(diagram):
    def remove_stacktrace(error_message):
        # split into lines
        lines = error_message.split("\n")
        # remove lines that contain "https://cdn.jsdelivr.net"
        new_lines = [line for line in lines if "https://cdn.jsdelivr.net" not in line]
        # join the lines back together
        return "\n".join(new_lines)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Set up the HTML template with the Mermaid diagram
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        </head>
        <body>
        <script>
        const diagram = `{diagram}`;
        let isValid = false;
        let errorMessage = '';
        try {{
            isValid = mermaid.parse(diagram);
        }} catch (err) {{
            errorMessage = err.message;
        }}
        </script>
        </body>
        </html>
        """

        # Set the page content
        await page.set_content(html)

        try:
            # Wait for the parsing result
            parsing_result = await page.evaluate('isValid')
            error_message = ""
        except Exception as e:
            parsing_result = False
            error_message = remove_stacktrace(str(e))

        await browser.close()

        if parsing_result:
            return True, "Valid Mermaid diagram"
        else:
            return False, error_message or "Invalid Mermaid diagram"