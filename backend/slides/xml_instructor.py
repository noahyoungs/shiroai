import re
from typing import Type, List, Dict, Optional
from pydantic import BaseModel, ValidationError, root_validator
from lxml import etree
from inflection import underscore, ordinalize, singularize
from typing import Any, Type, Union
from pydantic_async_validation import AsyncValidationModelMixin


def clean_xml(text):

    # Step 0: Remove all HTML comments
    # text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Step 1: Find all the opening tags, closing tags, and create a list of dicts
    pattern = re.compile(r'<(?!\!--)[^>]+>')
    tags = pattern.finditer(text)
    tag_list = []
    for tag in tags:
        tag_name = tag.group()[1:-1].split()[0]
        is_opening = not tag.group().startswith('</')
        is_opening = not tag.group().startswith('</')
        if not is_opening:
            tag_name = tag_name[1:]  # Remove the '/' from the closing tag
        tag_dict = {
            'name': tag_name,
            'is_opening': is_opening,
            'index': tag.start() if is_opening else tag.end()
        }
        tag_list.append(tag_dict)

    # drop any br tags
    tag_list = [tag for tag in tag_list if 'br' not in tag['name']]

    # print(tag_list)

    # Step 2: Error if each opening tag doesn't have a corresponding closing tag
    tag_counts = {}
    for tag in tag_list:
        tag_name = tag['name']
        if tag_name not in tag_counts:
            tag_counts[tag_name] = {'opening': 0, 'closing': 0}
        if tag['is_opening']:
            tag_counts[tag_name]['opening'] += 1
        else:
            tag_counts[tag_name]['closing'] += 1

    for tag_name, counts in tag_counts.items():
        if counts['opening'] != counts['closing']:
            raise ValueError(f"Mismatched tags for <{tag_name}>")

    # Step 3: Error if the same opening tag appears before the first one was closed
    open_tags = []
    for tag in tag_list:
        if tag['is_opening']:
            if tag['name'] in open_tags:
                raise ValueError(
                    f"Nested tags with the same name <{tag['name']}> are not allowed.")
            open_tags.append(tag['name'])
        else:
            if not open_tags or tag['name'] != open_tags[-1]:
                raise ValueError(f"Mismatched closing tag </{tag['name']}>")
            open_tags.pop()

    # Step 4: Create an empty string for the output text and iterate through the list of identified tags
    output_text = ""
    index = 0
    while index < len(tag_list):
        if tag_list[index]['is_opening']:
            opening_tag = tag_list[index]
            closing_tag = None
            for i in range(index + 1, len(tag_list)):
                if not tag_list[i]['is_opening'] and tag_list[i]['name'] == opening_tag['name']:
                    closing_tag = tag_list[i]
                    break
            if closing_tag:
                output_text += text[opening_tag['index']:closing_tag['index']]
                index = i + 1
            else:
                raise ValueError(
                    f"Mismatched opening tag <{opening_tag['name']}>")
        else:
            index += 1

    return output_text


def generate_xml_string(model_class: Union[Type[BaseModel], dict], data: Any,) -> str:
    xml_string = ""

    if isinstance(model_class, dict):
        schema = model_class
    else:
        schema = model_class.schema()

    if isinstance(data, dict):
        for field_name, field_value in data.items():
            field_info = schema['properties'][field_name]
            field_type = field_info.get('type')

            if field_type == 'object':
                ref = field_info.get('$ref')
                if ref:
                    singular_name = ref.split('/')[-1]
                    singular_name_underscore = underscore(singular_name)
                    item_model_schema = schema['$defs'][singular_name]
                    if len(list(item_model_schema['properties'].values())) > 1:
                        xml_string += f"<{singular_name_underscore}>\n"
                    xml_string += generate_variable_input_xml(
                        item_model_schema, schema)
                    if len(list(item_model_schema['properties'].values())) > 1:
                        xml_string += f"\n</{singular_name_underscore}>\n"
                    else:
                        xml_string += f"\n"
                else:
                    xml_string += f"<{field_name}>\n"
                    xml_string += generate_xml_string(field_info, field_value)
                    xml_string += f"</{field_name}>\n"

            elif field_type == 'array':
                xml_string += f"<{field_name}>\n"
                for item in field_value:
                    items_info = field_info['items']
                    ref = items_info.get('$ref')
                    if ref:
                        singular_name = ref.split('/')[-1]
                        singular_name_underscore = underscore(singular_name)
                        item_model_schema = schema['$defs'][singular_name]
                        xml_string += f"<{singular_name_underscore}>\n"
                        xml_string += generate_xml_string(
                            item_model_schema, item)
                        xml_string += f"\n</{singular_name_underscore}>\n"
                xml_string += f"</{field_name}>\n"
            else:
                if field_value is not None:
                    xml_string += f"<{field_name}>\n{field_value}\n</{field_name}>\n"

    else:
        xml_string += f"{data}\n"

    return xml_string.strip()


def generate_example_xml(model_class: Type[BaseModel]) -> str:
    example_data = model_class.Config.json_schema_extra.get("example", {})
    xml_string = generate_xml_string(model_class, example_data)
    return xml_string


def generate_xml_from_instance(model_instance: BaseModel) -> str:
    model_class = type(model_instance)
    data = model_instance.dict()
    xml_string = generate_xml_string(model_class, data)
    return xml_string


def restore_line_breaks(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = restore_line_breaks(value)
    elif isinstance(data, list):
        return [restore_line_breaks(item) for item in data]
    elif isinstance(data, str):
        return data.replace("LINE_BREAK!", "<br>")
    return data


def parse_xml_to_model(xml_string: str, model_class: Type[BaseModel], **kwargs) -> BaseModel:

    # Escape &
    xml_string = xml_string.replace("&", "&amp;")
    xml_string = re.sub(r"<br\s*/?>", "LINE_BREAK!", xml_string)

    # Extract the XML string between the root tags
    xml_string = clean_xml(xml_string)

    # Parse the XML string
    try:
        root = etree.fromstring(f"<root>{xml_string}</root>")
    except etree.XMLSyntaxError as e:
        print(f"Invalid XML: {str(e)}")
        print(f"XML: {xml_string}")
        raise ValueError(f"Invalid XML: {str(e)}")

    # Get the schema of the model class
    schema = model_class.schema()
    # print(f"Whole Schema: {schema}")

    # Initialize a dictionary to store the parsed data
    data = {}

    # Recursively parse the XML elements based on the schema
    def parse_element(element, schema_prop):
        # print(f"Element: {element.tag}")
        # print(f"Schema: {schema_prop}")

        if 'anyOf' in schema_prop:
            schema_prop['type'] = schema_prop['anyOf'][0]['type']
            if schema_prop['anyOf'][0].get('items'):
                schema_prop['items'] = schema_prop['anyOf'][0]['items']
            # print(f"Found anyOf, using {schema_prop['type']} as type")

        if 'type' in schema_prop:
            if schema_prop['type'] == 'array':
                # print(f"Array: {element.tag}")
                return [parse_element(child, schema_prop['items']) for child in element]
            elif schema_prop['type'] == 'object':
                # print(f"Object: {element.tag}")
                if len(list(schema_prop['properties'].values())) == 1 and element.tag == list(schema_prop.get('properties', {}).keys())[0]:
                    # print(f"Match! {element.tag} == {list(schema_prop.get('properties', {}).keys())[0]}")
                    return {element.tag: parse_element(element, list(schema_prop['properties'].values())[0])}
                else:
                    return {child.tag: parse_element(child, schema_prop['properties'][child.tag]) for child in element}
            else:
                # print(f"Element: {element.tag}")
                return element.text.strip()
        elif '$ref' in schema_prop:
            # print(f"Ref: {schema_prop['$ref']}")
            ref_name = schema_prop['$ref'].split('/')[-1]
            ref_schema = schema['$defs'][ref_name]
            return parse_element(element, ref_schema)

    # Parse the root element based on the schema
    for child in root:
        try:
            data[child.tag] = parse_element(
                child, schema['properties'][child.tag])
        except KeyError as e:
            print(f"KeyError: {str(e)}")
            print(
                f"Warning: {child.tag} was found in the xml but does not belong in the pydantic model. Skipping...")

    # add the kwargs to any dicts in lists
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item.update(kwargs)

    # Merge the parsed data with the provided keyword arguments
    data.update(kwargs)

    # Restore LINE_BREAK! placeholders to <br> tags
    data = restore_line_breaks(data)

    # Create an instance of the model class using the parsed data and keyword arguments

    # print(f"Data: {data}")
    model_instance = model_class(**data)
    return model_instance


def truncate_input(input_str):
    if len(input_str) <= 40:
        return input_str
    else:
        return input_str[:20] + "..." + input_str[-17:]


def get_val_error_string(errors: dict) -> str:
    error_string = "Please fix the following issues with your previous response:\n\n"
    for error in errors:
        # print(error)
        if isinstance(error['input'], str):
            input_string = truncate_input(error['input'].strip())
        else:
            input_string = ""
        if len(error['loc']) == 3:
            index_word = ordinalize(error['loc'][1] + 1)
            locator_string = f"{index_word} <{error['loc'][2]}></{error['loc'][2]}> in the <{error['loc'][0]}></{error['loc'][0]}>"
        if len(error['loc']) == 2:
            print("Loc length 2")
            locator_string = f"<{error['loc'][0]}></{error['loc'][0]}>"
        elif len(error['loc']) == 1:
            locator_string = f"<{error['loc'][0]}></{error['loc'][0]}>"

        if error['type'] == 'string_too_short':
            required_length = list(error['ctx'].values())[0]
            error_string += f"- The {locator_string} you provided contains {len(error['input'])} characters, but the minimum allowed is {required_length} characters. Please add {required_length - len(error['input'])} or more characters.\n"
        elif error['type'] == 'string_too_long':
            allowed_length = list(error['ctx'].values())[0]
            error_string += f"- The {locator_string} you provided contains {len(error['input'])} characters, but the maximum allowed is {allowed_length} characters. Please remove {len(error['input']) - allowed_length} or more characters.\n"
        elif error['type'] == 'missing':
            error_string += f"- {locator_string} was not found. Please provide a valid value for {locator_string}.\n"
        elif error['type'] == 'too_long':
            error_string += f"- The {locator_string} {error['ctx']['field_type'].lower()} you provided contains {error['ctx']['actual_length']} items, but the maximum allowed is {error['ctx']['max_length']} items. Please remove {error['ctx']['actual_length'] - error['ctx']['max_length']} or more items.\n"
        elif error['type'] == 'too_short':
            error_string += f"- The {locator_string} {error['ctx']['field_type'].lower()} you provided contains {error['ctx']['actual_length']} items, but the minimum allowed is {error['ctx']['min_length']} items. Please add {error['ctx']['min_length'] - error['ctx']['actual_length']} or more items.\n"
        elif error['type'] == 'literal_error':
            error_string += f"- The {locator_string} must be {error['ctx']['expected']}. Your input '{input_string}' is not allowed. Please provide a valid value for {locator_string}.\n"
        elif error['type'] == 'int_parsing':
            error_string += f"- The {locator_string} you provided must be an integer. Your input '{input_string}' is not a valid integer. Please provide a valid integer for {locator_string}.\n"
        elif error['type'] == 'value_error':
            error_string += f"- {error['msg']}\n"
        else:
            error_string += f"- [{'.'.join([str(field) for field in error['loc']])}]: {error['msg']}\n"
            # error_string += f"- {locator_string}: {error['msg']}\n"

    return error_string


def parse_response_tags(text):
    pattern = r'<response>(.*?)</response>'
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches) == 0:
        raise ValueError(
            f"You are missing the <response></response> tags in your response. Please provide a valid <response></response> with your response to the user.")
    elif len(matches) > 1:
        raise ValueError(
            f"You have more than one <response></response> tags in your response. Please provide only one <response></response> with your response to the user.")
    elif len(matches[0].strip()) == 0:
        raise ValueError(
            f"Your <response></response> is empty. Please provide a valid <response></response> to the user.")
    return matches[0].strip()


async def get_basemodel_instance_from_llm(client, pydantic_model_class, dynamic_val_params={}, max_iterations=5, stop_on_last_tag_close=True, force_start_with_first_tag=True, temperature=0.5, temperature_multiplier=None, max_temperature=2, error_message_prefix=None, **kwargs):
    """
    Asynchronously generate a Pydantic model instance from an LLM response.

    This function interacts with an LLM to generate XML content that conforms to a specified Pydantic model.
    It handles validation, error correction, and can adjust generation parameters over multiple iterations.

    Parameters:
    - client: The LLM client used for generating responses.
    - pydantic_model_class (Type[BaseModel]): The Pydantic model class to instantiate.
    - dynamic_val_params (dict): Additional parameters for dynamic validation. Default is an empty dict.
    - max_iterations (int): Maximum number of attempts to generate a valid response. Default is 5.
    - stop_on_last_tag_close (bool): If True, stops generation at the closing tag of the last field. Default is True.
    - force_start_with_first_tag (bool): If True, ensures the response starts with the opening tag of the first field. Default is True.
    - temperature (float): Initial temperature for LLM generation. Default is 0.5.
    - temperature_multiplier (float): Factor to increase temperature in each iteration. Default is None.
    - max_temperature (float): Maximum allowed temperature. Default is 2.
    - error_message_prefix (str): Prefix for error messages sent to the LLM on retries when pydantic valideation fails. Default is None.
    - **kwargs: Additional keyword arguments for the LLM client, including 'messages' and 'stop'.

    Returns:
    - tuple: A tuple containing:
        1. The instantiated Pydantic model
        2. The final list of messages used in the conversation

    Raises:
    - ValueError: If no initial messages are provided.
    - RuntimeError: If max_iterations is reached without a valid response.
    - Other exceptions may be raised during XML parsing or model validation.

    Notes:
    - The function uses a retry mechanism, adjusting parameters and providing feedback on errors to the LLM.
    - It handles XML generation, parsing, and Pydantic model instantiation.
    - Supports both standard Pydantic models and those inheriting from AsyncValidationModelMixin.
    - Temperature can be dynamically adjusted across iterations to potentially improve response quality.

    Example usage:
    ```
    client = AsyncOpenAI()
    model_instance, messages = await get_basemodel_instance_from_llm(
        client,
        MyPydanticModel,
        messages=[{"role": "user", "content": "Generate a response"}],
        temperature=0.7
    )
    ```
    """
    
    if error_message_prefix is None:
        error_message_prefix = ""
    else:
        error_message_prefix = f"{error_message_prefix}\n"

    first_tag_name = (list(pydantic_model_class.schema()['properties'].values())[
                      0]['title']).lower().replace(' ', '_')
    last_tag_name = (list(pydantic_model_class.schema()[
                     'properties'].values())[-1]['title']).lower().replace(' ', '_')

    messages = kwargs.get("messages", [])
    if len(messages) == 0:
        raise ValueError(
            "You must provide at least one message to start the conversation.")

    stop = kwargs.get("stop", [])

    if stop_on_last_tag_close:
        # the last closing tag were looking for
        stop.append(f"</{last_tag_name}>")

    iteration = 0
    while iteration < max_iterations:

        if temperature_multiplier:
            current_temperature = min(
                temperature * (temperature_multiplier ** iteration), max_temperature)
        else:
            current_temperature = temperature

        temp_messages = messages.copy()

        if force_start_with_first_tag:
            temp_messages.append(
                {"role": "assistant", "content": f"<{first_tag_name}>"})

        response = await client.chat.completions.create(
            messages=temp_messages,
            stop=stop or None,
            temperature=current_temperature,
            # kwargs without messages
            **{key: value for key, value in kwargs.items() if key != "messages"}
        )

        response_text = response.choices[0].message.content.strip()

        if force_start_with_first_tag:
            if not response_text.startswith(f"<{first_tag_name}>"):
                response_text = f"<{first_tag_name}>{response_text}"

        if stop_on_last_tag_close:
            if f"<{last_tag_name}>" in response_text:
                if not response_text.endswith(f"</{last_tag_name}>"):
                    response_text += f"</{last_tag_name}>"

        try:
            messages.append({"role": "assistant", "content": response_text})
            model_instance = parse_xml_to_model(
                response_text, pydantic_model_class, **dynamic_val_params)
            if issubclass(pydantic_model_class, AsyncValidationModelMixin):
                await model_instance.model_async_validate()
            print(f"Completed in {iteration + 1} iterations.")
            return model_instance, messages
        except Exception as e:
            if isinstance(e, ValidationError):
                error_string = get_val_error_string(e.errors())
                print(f"LLM Mistake: {error_string}")
                messages.append({"role": "user", "content": f"{error_message_prefix}{error_string}"})
            elif isinstance(e, ValueError):
                print(f"LLM Mistake: {str(e)}")
                messages.append({"role": "user", "content": f"{error_message_prefix}There was a syntax issue with the XML you provided:\n{str(e)}\n\nPlease fix your XML response. This error might be caused because you inadvertently used an XML tag as part of your response. In this case, please only use XML tags for the input fields, and if you must use XML tags in your response, please use them in pairs. (e.g. <tag></tag> instead of <tag>)"})
            else:
                raise e

            iteration += 1
            continue

    raise RuntimeError(
        f"Maximum number of iterations ({max_iterations}) reached without obtaining a valid response.")


def generate_variable_input_xml(model_class: Union[Type[BaseModel], dict], schema: Optional[dict] = None) -> str:
    xml_string = ""

    if isinstance(model_class, dict):
        schema = model_class
    else:
        if schema is None:
            schema = model_class.schema()

    for field_name, field_info in schema.get('properties', {}).items():
        field_type = field_info.get('type')

        if field_type == 'object':
            ref = field_info.get('$ref')
            if ref:
                nested_model_name = ref.split('/')[-1]
                nested_model_schema = schema['$defs'][nested_model_name]
                xml_string += f"<{nested_model_name.lower()}>\n"
                xml_string += generate_variable_input_xml(
                    nested_model_schema, schema)
                xml_string += f"</{nested_model_name.lower()}>\n"
            else:
                xml_string += f"<{field_name}>\n"
                xml_string += generate_variable_input_xml(field_info, schema)
                xml_string += f"</{field_name}>\n"
        elif field_type == 'array':
            xml_string += f"<{field_name}>\n"
            items_info = field_info['items']
            ref = items_info.get('$ref')
            if ref:
                singular_name = ref.split('/')[-1]
                singular_name_underscore = underscore(singular_name)
                item_model_schema = schema['$defs'][singular_name]
                if len(list(item_model_schema['properties'].values())) > 1:
                    xml_string += f"<{singular_name_underscore}>\n"
                xml_string += generate_variable_input_xml(
                    item_model_schema, schema)
                if len(list(item_model_schema['properties'].values())) > 1:
                    xml_string += f"\n</{singular_name_underscore}>\n"
                else:
                    xml_string += f"\n"
            xml_string += f"{{{{ADDITIONAL_{field_name.upper()}}}}}"
            xml_string += f"\n</{field_name}>\n"
        else:
            xml_string += f"<{field_name}>\n"
            xml_string += f"{{{{{field_name.upper()}}}}}"
            xml_string += f"\n</{field_name}>\n"

    return xml_string.strip()


def create_dynamic_enum_validator(values_key: str, field_name: str, error_template: Optional[str] = None):
    def validator(cls, values):
        field_value = values.get(field_name)
        valid_values = values.get(values_key)

        if valid_values is None:
            print(
                f"Warning: {values_key} not provided. Not validating {field_name}.")
        elif field_value not in valid_values:
            if error_template:
                error_message = error_template.format(
                    field_name=field_name, field_value=field_value)
            else:
                error_message = f"<{field_name}>{field_value}</{field_name}> is not valid. Please provide a valid <{field_name}></{field_name}>."
            raise ValueError(error_message)

        return values

    return root_validator(pre=True)(validator)


def create_dynamic_enum_validator(values_key: str, field_name: str, error_template: Optional[str] = None):
    def validator(cls, values):
        field_value = values.get(field_name)
        valid_values = values.get(values_key)

        if valid_values is None:
            print(
                f"Warning: {values_key} not provided. Not validating {field_name}.")
        elif field_value not in valid_values:
            if error_template:
                error_message = error_template.format(
                    field_name=field_name, field_value=field_value)
            else:
                error_message = f"<{field_name}>{field_value}</{field_name}> is not valid. Please provide a valid <{field_name}></{field_name}>."
            raise ValueError(error_message)

        return values

    return root_validator(pre=True)(validator)


def create_dynamic_enum_list_validator(values_key: str, field_name: str, error_template: Optional[str] = None):
    def validator(cls, values):
        field_value = values.get(field_name)
        valid_values = values.get(values_key)

        if valid_values is None:
            print(
                f"Warning: {values_key} not provided. Not validating {field_name}.")
        elif not isinstance(field_value, list):
            error_message = f"{field_value} must be a list in order to use create_dynamic_enum_list_validator."
            raise ValueError(error_message)
        else:
            invalid_items = [
                item for item in field_value if item not in valid_values]
            if invalid_items:
                if len(invalid_items) > 1:
                    if error_template:
                        error_message = error_template.format(
                            field_name=field_name, invalid_items=invalid_items)
                    else:
                        error_message = f"<{field_name}>{invalid_items[0]}</{field_name}> and {len(invalid_items)-1} other <{field_name}></{field_name}> you provided are not valid. Please provide valid <{field_name}></{field_name}>."
                else:
                    if error_template:
                        error_message = error_template.format(
                            field_name=field_name, invalid_item=invalid_items)
                    else:
                        error_message = f"<{field_name}>{invalid_items[0]}</{field_name}> is not valid. Please provide a valid <{field_name}></{field_name}> instead."

                raise ValueError(error_message)

        return values

    return root_validator(pre=True)(validator)
