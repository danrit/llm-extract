# Generate a complete Markdown documentation of Cloudflare Transformation URL API reference.

The complete documentation of Cloudflare Transformation is available on their website: page [Features - Cloudflare Images docs](https://developers.cloudflare.com/images/optimization/features/) (local copy of the documentation is available in [cloudflare.html](./cloudflare.html))

On the same page, there is a link to a markdown version of the documentation but it is not ideal because it contains links to image examples (want to generate a text-only documentation) and the syntax used to exposed both the "URL format" and "Workers" approaches is broken.

The goal is to generate a markdown documentation of the cloudflare image transformation features, actually limited to the information available in the page.
 
Specifically, here are some requirements about what should be removed and what should be kept:

- Remove any navigation elements
- Remove images examples
- For the embedded code snippets: keep ONLY the "URL format" version of the code snippet, ie remove the "Workers"/Javascript version.
- keep anchor links

Best to generate a parsing script (`parse_cloudflare.py`) to do that and apply it to the local copy of the documentation (`cloudflare.html`) to generate a markdown version of the documentation. I think it is a more reliable way.

Output the generated markdown documentation in a file named `cloudflare.md`.
