# README

Example use case: Migrating 6 url-based image transformations from Service A to Service B (Cloudinary to Cloudflare): both provide the same feature but the syntax is different. IN the example the starting point is:
- a chain of transformations in Service A
- the documentation of Service A
- the documentation of Service B

The goal is to find the equivalent chain of transformations in Service B. Trying to use some "simple" transformations (resizing, cropping, format conversion): this is not a test of the services capabilities.

## Config

Overview of this example configuration set in `config.yaml` file:

- Declare the dataset file and the documents (see Data section below)
- Declare the prompt file (see Prompt section below)
- Declare the data schema to extract (1 comma-separated string)
- Define a few LLM available (Deepseek-R1, gemma3 and opt-oss)
- Specify the scenario to run: specify the dataset and the schema to use and a combination variable parameters: documents, prompts, models + some run parameters

## Data

- dataset.jsonl: the list of 5 transformations
- The `documents` folder contains:
    - references documentation for both services in Markdown format.

### notes on Cloudinary and Cloudflare documentation

**Cloudinary**

The website documentation of cloudinary is complete on [Transformation URL API reference](https://cloudinary.com/documentation/transformation_reference) but the HTML document downloaded is 4.5MB! There is link to a markdown version of the documentation but it is useless because information are truncated. (June-2026)

**Cloudflare**

The documentation of cloudflare image transformation is available on their website: [Features - Cloudflare Images docs](https://developers.cloudflare.com/images/optimization/features/), the HTML document downloaded is 318KB. There is a link to the markdown version of the documentation, it is complete, but it contains link to image examples (don't want add image to the LLM input, that would be an entirely different experiment) and the syntax used to exposed both the "URL format" and "Workers" approaches is broken. (June-2026)

**Remediation**

I have used an agent to
- create a script to generate a complete markdown version of the documentation from the HTML version. The result is a 300KB markdown file: [cloudinary.md](./documents/cloudinary.md). 
- create a script to generate a workable markdown version of the documentation from the HTML version. The result is a 30KB markdown file: [cloudflare.md](./documents/cloudflare.md).

The initial prompts, the agent sessions (containing the conversation) and the produced scripts are available in `documents/process/` folder for reference.



### Choice of transformations

Defined a set of 6 transformations in Cloudinary UI console: Aiming for a mix of common and more complex transformations. 

- transformation 1: `c_auto,w_320/f_webp/q_auto:good`
- transformation 2: `e_brightness:35/a_180`
- transformation 3: `co_rgb:EE0F0F,l_text:Helvetica_100_normal_left:lorem%2520ipsum/fl_layer_apply,fl_no_overflow,g_south,y_30`
- transformation 4: `c_thumb,g_auto,h_320,w_320,z_1`
- transformation 5: `c_fill,h_360,w_640/e_saturation:-100`
- transformation 6: `b_rgb:333B4C,c_pad,h_640,w_640`

## Prompt

The prompt is in `data/example2-img-transform/PROMPT.default.md`
