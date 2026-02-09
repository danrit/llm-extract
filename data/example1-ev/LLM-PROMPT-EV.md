# LLM Prompt

## Context

```{doc_language}
{doc_content}
```

## Instruction

The goal is to extract structured data for 5 attributes (see below) of the electric vehicle "{full_model_name}", in configuration "{configuration_name}" available in {country_name} in the year {year} from unstructured text given as context.

The document given as a context beforehand is the wikipedia article for this Electrical Vehicle. The article contains potentially information about several configurations (or models, types) of the vehicle, several regional variants of the vehicle and several years of production of the vehicle.

The 5 electrical vehicle attributes to extract are:
 - battery capacity (kWh): the value in the text is always followed by "kWh". Usually below 200 kWh.
 - charging power AC (kW)
 - charging power DC (kW)
 - power (kW)
 - range WLTP (km)

If there are multiple values for an attribute, prefer the one most applicable for the given criteria of configuration, country and year. If no contextual information is available about the criteria use the generic value for the vehicle.

If the text does not contain the information or is ambiguous for an attribute, return "null" for that attribute.

Format the data in the response as a JSON Markdown fenced code block with the following keys:
 - battery_capacity
 - charging_AC
 - charging_DC
 - power
 - range

Example output:

```json
{{
  "battery_capacity": 70.5,
  "charging_ac": 11,
  "charging_dc": 150,
  "power": 210,
  "range": 570
}}
```
