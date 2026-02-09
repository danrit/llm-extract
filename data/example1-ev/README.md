# README

Example use case: Extracting 5 electrical vehicle attributes (battery capacity, range, power, charging power AC , charging power DC) from 12 Wikipedia articles on Electric Vehicles (EVs).

## Config

Overview of this example configuration set in `config.yaml` file:

- Declare the dataset file and the documents (see Data section below)
- Declare the prompt file (see Prompt section below)
- Declare the data schema to extract (5 EV attributes)
- Define a few LLM available (Deepseek-R1, gemma3 and opt-oss)
- Specify the scenario to run: specify the dataset and the schema to use and a combination variable parameters: documents, prompts, models + some run parameters

## Data

- dataset.jsonl: the list of 12 EV models with appropriate parameters for the prompt generation
- The `documents` folder contains:
    - 12 wikitext files, downloaded from Wikipedia AND simplified following the [wikitext steps below](#prepare-wiki-article-to-lite-html) _Intermediate step, not strictly necessary_ + `doc.wikitext.jsonl` which is a manifest of the 12 wikitext files
    - 12 HTML files, generated from the simplified wikitext files following the [HTML steps below](#steps-on-the-html-source) _Final input for the LLM_ + `doc.html.jsonl` which is a manifest of the 12 HTML files

### Choice of 12 EVs

Roughly based on 10 best-selling EVs in Australia in 2024:
- Tesla Model Y
- Tesla Model 3
- MG 4
- BYD Seal
- BYD Atto 3
- BMW iX1 (see wiki article BMW X1 (U11))
- Volvo EX30
- BYD Dolphin
- BMW i4
- Kia EV6

Plus 2 miscellaneous:
- XPeng G6
- BYD Sealion 6 (see wiki article BYD Song Plus)

Pulled from en.wikipedia.org on 2025-09-26.

### Prepare wiki article to lite html

Data preparation steps done to get a lite version of the wiki article in HTML format used in this example.

#### Steps on the wikitext source

1. remove all ref elements:
   1. `<ref[^>]*?/>` (self-closing ref tags)
   2. `<ref[^>]*?>.*?<\/ref>` (ref tags with content)
2. wikilinks:
   1. Replace all the wiki links `[[...]]` with just the display text (if any): `\[\[(?!File:)(?:[^|\]]+\|)?([^\]]+)\]\]` replace with `$1`
   2. Remove all file links: `\[\[File:[^\]]+\]\]` replace with ``
3. Remove all gallery tags and content: `<gallery\b[^>]*>[\s\S]*?<\/gallery>` replace with ``
4. Delete Reference, external links, See also sections and categories at the end of the article 

#### Render to HTML

1. copy and paste the cleaned wikitext in the edit page of a wikimedia editor
2. Generate the preview
3. In the inspector view, locate the portion of the page for the article content and copy it

#### Steps on the HTML source

1. paste the content in a text editor:
   1. replace all the links by their text only (remove the URL): `<a[^>]*>(.*?)</a>` replace with `$1`
2. remove all style attributes: ` style="[^"]*"` replace with ``
3. remove all style tags and content: `<style[^>]*?>.*?<\/style>` replace with ``
4. remove all tag attributes for all tags EXCEPT 'rowspan' and 'colspan': `\b(?!rowspan\b)(?!colspan\b)([a-zA-Z_:][a-zA-Z0-9_.:-]*)\s*=\s*(".*?"|'.*?'|[^\s>]+)` replace with ``
5. remove all img tags: `<img[^>]*>` replace with ``
6. Remove all div and span tags but keep their content:
   1. clean opening tags by removing extra spaces: `<(div|span)\b *[^>]>` replace with `<$1>`
   2. Remove opening and closing tags: `<\/?(div|span)>` replace with ``
7. Insert the cleaned HTML snippet in a simple HTML template like below:
   1. update the title and h1 tag with the vehicle name
   2. save as .html file

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        /* Add border for table */
        table, th, td {
        background-color: var(--background-color-neutral-subtle, #f8f9fa);
        color: var(--color-base, #202122);
        margin: 1em 0;
        border: 1px solid var(--border-color-base, #a2a9b1);
        border-collapse: collapse;
        }
    </style>
</head>
<body>
    <h1>Title</h1>
    {html_snippet}
</body>
</html>
```

Note: Contains light styling for table readability.

## Prompt

The prompt is in `data/example1-ev/LLM-PROMPT-EV.md` and contains instructions to extract the 5 attributes from the content of the wiki article.
