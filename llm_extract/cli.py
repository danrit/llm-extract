import argparse
import json
import llm
import ollama
import yaml
from llm_extract.ollama_ollama import ollama_ollama_call
from llm_extract.simonw_llm import simonw_llm_call

parser = argparse.ArgumentParser(
    description="Extract structured data from raw content using LLM.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="keep LLM prompts, responses, execution time (+...)")
parser.add_argument('-c', '--configfile', default='config.yaml',
                    help="Specify the configuration file to use (default: config.yaml)")
parser.add_argument('--scenario', default='default',
                    help="Specify the scenario to run (see config.yaml)")
args = parser.parse_args()

# HEREHERE:
# - clean output folder and commit...

# Ollama-powered models all accept the Ollama modelfile parameters as options
# see: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameter

# trying to stick to [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
### HEREHEREHERE: now that config.json is defined: update that script...
_LLM_CONFIGS = {
    1: {
        'model': 'DeepSeek-R1-Distill-Llama-8B-Q4_0',
        'options': {
            # max_tokens: default is 200?. need more to get non-truncated
            # response for lots of scenario
            'max_tokens': 8192,
            # temp and top_p: set to Recommended values, see:
            # https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B
            # Notes: the response is still a bit random, but it outputs the
            # expected JSON for the 1 example. so that is just the situation.
            # Maybe or maybe not need tweaking later
            'temp': 0.6,
            'top_p': 0.95,
        }
    },
    2: {
         'model': 'gemma3',
            'options': {
                'num_predict': 8192,
                'temperature': 0, # 0;0.5;1
                'top_p': 0.1 # 0.1;0.5;0.95
            }
    },
    3: {
        'model': 'gpt-oss',
        'options': {
            'num_predict': 8192,
            'temperature': 0,  # 0;0.5;1
            'top_p': 0.1  # 0.1;0.5;0.95
        }
    },
    4: {
        'model': 'deepseek-r1:8b-llama-distill-q4_K_M',
        'options': {
            'num_predict': 8192,
            'temperature': 0,  # 0;0.5;1
            'top_p': 0.1  # 0.1;0.5;0.95
        }
    },
}
_SELECTED_LLM = 4

_PROMPT_TEMPLATE_PATH = './LLM-PROMPT.md'
_OUTPUT_DIR = './output'


def build_prompt(template: str, variables: dict) -> str:
    """ Template processing function to build the prompt.

    :param template:
    :param variables:
    :return:
    """
    # if on of the data field follow the naming <var>_filename,
    # load the file content into a new field <var>:
    variables_loaded = {}
    for k, v in variables.items():
        if k.endswith('_filename'):
            var_name = k[:-9]  # remove _filename
            with open(v, 'r') as file:
                variables_loaded[var_name] = file.read()
        else:
            variables_loaded[k] = v

    prompt = template.format(**variables_loaded)
    # for k, v in vars.items():
    #     placeholder = f'<{k}>'
    #     prompt = prompt.replace(placeholder, v)

    return prompt


def call_llm(prompt: str, model_config: dict, model_options: dict) -> dict:
    # generate options by mapping model_options keys to model specific option keys
    model_options_specific = {}
    for key, value in model_options.items():
        if key in model_config['options']:
            model_options_specific[model_config['options'][key]] = value

    # call appropriate backend
    if model_config['backend'] == 'ollama_ollama':
        return ollama_ollama_call(prompt, model_config['name'],
                                  model_options_specific)
    elif model_config['backend'] == 'simonw_llm':
        return simonw_llm_call(prompt, model_config['name'],
                               model_options_specific)
    else:
        raise ValueError(f"Unknown backend: {model_config['backend']}")


def extract_structured_data(prompt_template: str, prompt_args: dict, llm_config: dict) -> dict:

    prompt = build_prompt(prompt_template, prompt_args)

    # DEBUG: output the prompt to a file
    with open('./output/debug-prompt.md', 'w') as file:
        file.write(prompt)
    # return {}

    response = call_llm(prompt, llm_config)

    # debug: output the response in json format to a file
    with open(f'{_OUTPUT_DIR}/debug-response.json', 'w') as file:
        json.dump(response, file, indent=2)

    # debug: print the response text
    print(response['data']['text'])

    return response
    output = {
        'data': {
            'attr1': 'value1',
            'attr2': 'value2'
        },
        'meta': {
            'success': True,
            'prompt_tokens': 123,
            'response_tokens': 456,
            'execution_time': 148
        },
    }

    return output


def run_variations(data: dict, variations: dict, config: dict):
    # print('data:', json.dumps(data, indent=2))
    # print('data_schema:', json.dumps(data_schema, indent=2))
    # print('variations:', json.dumps(variations, indent=2))
    # iterate over the prompts
    for prompt_name in variations['prompts']:
        # load the prompt definition
        prompt_config = config['prompts'][prompt_name]
        # load the file whose name is in prompt_config['template']['filename']
        with open(prompt_config['template']['filename'], 'r') as file:
            prompt_template = file.read()

        prompt = build_prompt(prompt_template, data)

        # debug: output the prompt to a file
        fmn_snake = data['full_model_name'].lower().replace(' ', '_')
        cn_snake = data['configuration_name'].lower().replace(' ', '_')
        # with open(f'./output/debug-prompt-{fmn_snake}-{cn_snake}-{prompt_name}.md', 'w') as file:
        #     file.write(prompt)

        # iterate over the models
        for model_name in variations['models']:
            model_config = config['models'][model_name]
            # add key 'name' to model_config if not present
            if 'name' not in model_config:
                model_config['name'] = model_name

            # iterate over the model options temperature and top_p
            for temp in variations['model_options']['temperature']:
                for top_p in variations['model_options']['top_p']:
                    model_options = {
                        'temperature': temp,
                        'top_p': top_p,
                        # Hard-coded max tokens (never part of the variations)
                        # TODO: move somewhere else?
                        'max_predict_tokens': 8192,
                    }

                    # iterate over the number of runs
                    for run in range(1, variations['runs'] + 1):
                        print(f'Run {run} of {variations["runs"]} for {fmn_snake} - {cn_snake}  prompt={prompt_name}, model={model_name}, temp={temp}, top_p={top_p} ')
                        print(model_options, model_config)
                        # HEREHEREHERE
                        response = call_llm(prompt, model_config, model_options)

                        # debug: output the response in json format to a file
                        with open(f'{_OUTPUT_DIR}/response-{fmn_snake}-{cn_snake}-{prompt_name}-{model_name}-temp{temp}-topp{top_p}-run{run}.json', 'w') as file:
                            file.write(json.dumps(response, indent=2))

    #                   HEREHEREHER: seems that it is working so far, now:
    #                   - extract json response and validate it against schema
    #                   - extract meta information (tokens, time, etc)
    #                   - aggregate results in a CSV or JSON file
    #                   - make it work with other backends (simonw/llm)


    return


# if __name__ == "__main__":
def cli():
    # extract_structured_data()
    # DEBUG
    # model = llm.get_model(_LLM_CONFIGS[_SELECTED_LLM]['model'])
    # response = model.prompt(
    #     'What is the capital of France?',
    #     **_LLM_CONFIGS[_SELECTED_LLM]['options']
    # )
    # # json_data = response.json()
    # # print(json_data)
    # print(response.text())
    # print(response.usage())


    # response = ollama.generate(
    #     model='gemma3',
    #     prompt='What is the capital of France?',
    #     options={'num_predict': 8192},
    #     stream=False
    # )
    #
    # # initiate meta with all attributes of response except response and context
    # meta = {k: v for k, v in vars(response).items() if k not in ['response', 'context']}
    # response_dict = {
    #     # 'data': {
    #     #     'text': response.text,
    #     # },
    #     'meta': meta,
    # }
    # print(json.dumps(response_dict, indent=2))

    # Load the config file config.yaml:
    with open(args.configfile, 'r') as file:
        config = yaml.safe_load(file)
    # print(data)

    if args.scenario not in config['scenarios']:
        print(f"Scenario '{args.scenario}' not found in config.yaml")
        exit(1)

    scenario = config['scenarios'][args.scenario]
    raw_data = config['raw_data'][scenario['raw_data']]
    data_schema = config['data_schema'][scenario['data_schema']]

    # print('variations:', json.dumps(scenario['variations'], indent=2))
    # print('data_schema:', json.dumps(data_schema, indent=2))
    combinations = []
    combinations_count = 1

    factor = len(scenario['variations']['prompts'])
    combinations_count *= factor
    combinations.append(f'{factor} prompt')

    factor = len(scenario['variations']['models'])
    combinations_count *= factor
    combinations.append(f'{factor} model')

    for parameter, values in scenario['variations']['model_options'].items():
        # print(f"Parameter: {parameter}, Values: {values}")
        # print(f'Total variations: {len(values)}')
        combinations_count *= len(values)
        combinations.append(f'{len(values)} {parameter}')

    factor = scenario['variations']['runs']
    combinations_count *= factor
    combinations.append(f'{factor} run')

    print(f'Total Variations: {combinations_count} ({" x ".join(combinations)})')

    # Iterate over the raw_data items:
    with open(raw_data['filename'], 'r') as infile:
        for line in infile:
            if not line.strip():
                continue
            # print(line.strip())
            data = json.loads(line.strip())
            run_variations(data, scenario['variations'], config)

    exit(0)

    with open(_PROMPT_TEMPLATE_PATH, 'r') as file:
        prompt_template = file.read()

    with open('input/xpeng_g6.html.old', 'r') as file:
        article = file.read()

    prompt_args = {
        'ARTICLE_HTML_CONTENT': article,
        'FULL_MODEL_NAME': 'Xpeng G6',
        'CONFIGURATION_NAME': 'Long Range',
        'COUNTRY_NAME': 'Australia',
        'YEAR': '2025',
    }

    extract_structured_data(prompt_template, prompt_args, _LLM_CONFIGS[_SELECTED_LLM])




