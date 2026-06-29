# Generate a complete Markdown documentation of Cloudinary Transformation URL API reference.

The complete documentation of Cloudinary Transformation URL API reference is available on their website: page [Transformation URL API reference](https://cloudinary.com/documentation/transformation_reference) (local copy of the documentation is available in [cloudinary.html](./cloudinary-truncated.html))

On thee same page, there is a link to a markdown version of the documentation but it is useless because information are truncated.

The goal is to generate a complete markdown documentation of the cloudinary transformation URL API reference, actually limited to the information available in the page.
 
Specifically, here are some requirements about what should be removed and what should be kept:

- Remove any navigation elements
- Remove images examples
- For the embeded code snippets: ideally keep ONLY the "URL" version of the code snippet.
- keep Syntax details table
- Remove the "Troubleshooting transformation errors" section.
- keep in-page links

Best to generate a parsing script to do that and apply it to the local copy of the documentation (cloudinary.html) to generate a markdown version of the documentation. I think it is a more reliable way.

Output the generated markdown documentation in a file named `cloudinary.md`.
