# LLM Prompt

## Context

Cloudinary is a SaaS company providing cloud media management services, specifically it includes an image transformation service. The service allows to transform images using a url-based API. The reference documentation of the service is given below.

Cloudflare is a company providing content delivery network services, specifically it includes an image transformation service. The service allows to transform images using a url-based API. The reference documentation of the service is given below.

The syntax of the transformation url is different between the two services.

{doc_1_markdown}
{doc_2_markdown}

TODO: here add a bit a more general templating system to pass a undefined number of embedded text documents: 2 ways to pass them:
- markdown documents; just plonk the markdown content in the prompt (like above)
- other text format: embedded them with a markdown code block with the language set to the format of the document (like for ev example)

## Instruction

**Cloudinary URL structure**:

The Cloudinary full delivery URL structure is: `https://res.cloudinary.com/<cloud_name>/<asset_type>/<delivery_type>/<transformations>/<version>/<public_id>.<extension>
cloudflare: https://<ZONE>/cdn-cgi/image/<OPTIONS>/<SOURCE-IMAGE>`

In that structure, the `<transformations>` component is the one that needs to be converted. The other components are not relevant for the conversion.

**Cloudflare URL structure**:

The Cloudflare full delivery URL structure (for a remote image, like in this context) is: `https://<ZONE>/cdn-cgi/image/<OPTIONS>/<SOURCE-IMAGE>`

In that structure, the `<OPTIONS>` component is the one that needs to be generated. The other components are not relevant for the conversion.

 **The goal is to convert the cloudinary transformation url to a cloudflare transformation url**.
 
The input is the Cloudinary transformation component `cloudinary_url_component={cloudinary_url_component}` the output is the equivalent transformation component of a cloudflare url `cloudflare_url_component`.


Example of Transformation component in Cloudinary and equivalent in Cloudflare:

|           | Cloudinary                             | Cloudflare                                 |
|-----------|----------------------------------------|--------------------------------------------|
| Example 1 | `c_thumb,g_north_west,h_320,w_320,z_1` | `fit=crop,gravity=0.0x0.0,h=320,w=320`     |
| Example 2 | `b_rgb:3448C5,c_pad,h_320,w_320`       | `background=%233448C5,fit=pad,h=320,w=320` |
| Example 3 | `q_auto:eco/f_avif/e_saturation:-100`  | `q=medium-low,f=avif,saturation=0`         |


For example 1 the full delivery urls are:
- Cloudinary: `https://res.cloudinary.com/dtl8ufrfi/image/upload/c_thumb,g_north_west,h_320,w_320,z_1/9.-Saghmosavank-church-in-winter-Haykhove-CCBYSA4.jpg` 
- Cloudflare: `https://info2007.xyz/cdn-cgi/image/fit=crop,gravity=0.0x0.0,h=320,w=320/images/9.-Saghmosavank-church-in-winter-Haykhove-CCBYSA4.jpg`

If a transformation component in Cloudinary does not have an equivalent in Cloudflare, return "null" for the output.

Example output:

```json
{{
  "cloudflare_url_component": "fit=crop,gravity=0.0x0.0,h=320,w=320"
}}
```
