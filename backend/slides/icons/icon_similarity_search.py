import numpy as np
import pandas as pd
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from langchain_openai import OpenAIEmbeddings
import os 
from dotenv import load_dotenv
import json

JSON_FILE = 'slides/icons/icon_data/icon_data.json'
EMBEDDINGS_DIR = 'slides/icons/icon_data/icon_embeddings'
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

load_dotenv()

# load emoji data from json file
with open(JSON_FILE, 'r') as f:
    extracted_data = json.load(f)
    
# initialize embeddings model
portkeyHeaders = createHeaders(
    provider="openai",
    api_key=os.getenv("PORTKEY_API_KEY"),
    config={"cache": {"mode":"simple"}},
)

openai_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)

valid_data = []
for i, d in enumerate(extracted_data):
    if d.get('icon_description') and len(d.get('use_cases', [])) == 3:
        valid_data.append(d)
        
# exclude any dicts where label starts with 'brand-'
valid_data = [d for d in valid_data if not d['original_label'].startswith('brand-')]        

# exclude any dicts where the lable starts with 'japanese-' and also ends with '-button'
valid_data = [d for d in valid_data if not (d['original_label'].startswith('japanese-') and d['original_label'].endswith('-button'))]


def cosine_similarity(vec1, vec2):
    """Compute the cosine similarity between two vectors.

    Args:
        vec1 (np.ndarray): The first vector.
        vec2 (np.ndarray): The second vector.

    Returns:
        float: The cosine similarity between vec1 and vec2.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
def get_reference_embeddings():
    """Generate or load reference embeddings for icon descriptions and use cases.

    Returns:
        tuple: A tuple containing grouped use case embeddings and icon description embeddings.
    """
        
    # assert that all the use_cases lists are of length 3
    for icon_data in valid_data:
        assert len(icon_data['use_cases']) == 3
        
    # flatten the list of use cases
    use_cases_flat = [use_case for icon_data in valid_data for use_case in icon_data['use_cases']]
    
    assert len(use_cases_flat) == len(valid_data) * 3

    icon_descriptions = [icon_data['icon_description'] for icon_data in valid_data]

    use_case_embeddings_path = os.path.join(EMBEDDINGS_DIR, 'use_case_embeddings.npy')
    icon_description_embeddings_path = os.path.join(EMBEDDINGS_DIR, 'icon_description_embeddings.npy')

    try:
        # Try loading the use case embeddings
        use_case_flat_embeddings = np.load(use_case_embeddings_path)
        
        # Try loading the icon description embeddings
        icon_description_embeddings = np.load(icon_description_embeddings_path)
        
        # Check if the loaded embeddings have the expected lengths
        if len(use_case_flat_embeddings) != len(valid_data) * 3 or len(icon_description_embeddings) != len(valid_data):
            raise ValueError("Loaded embeddings have unexpected lengths")
        
    except (FileNotFoundError, ValueError):
        print("Generating embeddings for all icons... This may take a few minutes.")
        # If loading fails or the lengths are unexpected, generate the embeddings
        
        # Vectorize the use cases
        use_case_flat_embeddings = np.array(openai_embeddings.embed_documents(use_cases_flat))
        
        # Save use case embeddings to .npy file
        np.save(use_case_embeddings_path, use_case_flat_embeddings)
        
        # Vectorize the icon descriptions
        icon_description_embeddings = np.array(openai_embeddings.embed_documents(icon_descriptions))
        
        # Save icon description embeddings to .npy file
        np.save(icon_description_embeddings_path, icon_description_embeddings)

    # regroup the embeddings by icon
    grouped_use_case_embeddings = []
    for i, icon_data in enumerate(valid_data):
        grouped_use_case_embeddings.append(use_case_flat_embeddings[i*3:i*3+3])
                
    return grouped_use_case_embeddings, icon_description_embeddings
        
    

async def similarity_search(query_embedding, grouped_use_case_embeddings, icon_description_embeddings):
    """Perform a similarity search for a given query embedding against icon embeddings.

    Args:
        query_embedding (np.ndarray): The query embedding to search for.
        grouped_use_case_embeddings (list): List of grouped use case embeddings for each icon.
        icon_description_embeddings (np.ndarray): Embeddings for icon descriptions.

    Returns:
        pd.DataFrame: DataFrame containing the sorted search results with similarity scores.
    """    
    
    df = pd.DataFrame(valid_data)
    
    # Average the vectors for the groups of use cases for each icon
    cosine_similarities = [cosine_similarity(np.mean(embeddings_for_icon_use_cases, axis=0), query_embedding) for embeddings_for_icon_use_cases in grouped_use_case_embeddings]

    df['use_case_cosine_similarity'] = cosine_similarities
            
    # compute cosine similarity between the bullet point embedding and the icon description embeddings
    cosine_similarities_icon_descriptions = [cosine_similarity(query_embedding, embedding) for embedding in icon_description_embeddings]
    
    df['icon_description_cosine_similarity'] = cosine_similarities_icon_descriptions
        
    combined_indicator_columns = ['use_case_cosine_similarity', 'icon_description_cosine_similarity']
    
    # Normalize the values for each metric to the range of -1 to 1
    normalized_df = df[combined_indicator_columns].apply(lambda x: (x - x.min()) / (x.max() - x.min()) * (2 - 1e-10) - 1 + 5e-11)
    
    combied_indicator = normalized_df[combined_indicator_columns].mean(axis=1)

    df['combined_indicator'] = combied_indicator
            
    df = df.sort_values('combined_indicator', ascending=False)
    
    # reindex df
    df = df.reset_index(drop=True)
    
    return df

# Run get_reference_embeddings when the Python file loads
grouped_use_case_embeddings, icon_description_embeddings = get_reference_embeddings()

async def choose_icons(bullet_point_text):
    """Choose the most similar icons for a given bullet point text.

    Args:
        bullet_point_text (str): The text of the bullet point.

    Returns:
        pd.DataFrame: DataFrame containing the sorted search results with similarity scores.
    """
    
    query_embedding = np.array(await openai_embeddings.aembed_query(bullet_point_text))

    return await similarity_search(query_embedding, grouped_use_case_embeddings, icon_description_embeddings)

async def choose_icons_from_embedding(query_embedding):
    """Choose the most similar icons for a given query embedding.

    Args:
        query_embedding (np.ndarray): The query embedding.

    Returns:
        pd.DataFrame: DataFrame containing the sorted search results with similarity scores.
    """
    
    return await similarity_search(query_embedding, grouped_use_case_embeddings, icon_description_embeddings)

async def get_most_similar_bp_to_icon(bullet_point_texts, bullet_point_embeddings, icon_original_label):
    """Get the index of the most similar bullet point to a given icon.

    Args:
        bullet_point_texts (list): List of bullet point texts.
        bullet_point_embeddings (np.ndarray): List of bullet point embeddings.
        icon_original_label (str): The original label of the icon.

    Returns:
        int: The index of the most similar bullet point.
    """
    
    if len(bullet_point_texts) == 0:
        return None
    assert len(grouped_use_case_embeddings) == len(icon_description_embeddings) == len(valid_data)
    assert len(bullet_point_texts) == len(bullet_point_embeddings)

    # look for the icon
    icon = [d for d in valid_data if d['original_label'] == icon_original_label][0]
    icon_index = valid_data.index(icon)

    if icon_index is None:
        raise ValueError(f"Icon with original label {icon_original_label} not found in the dataset.")

    # for icon
    use_case_embeddings = grouped_use_case_embeddings[icon_index]
    use_case_mean_embedding = np.mean(use_case_embeddings, axis=0)
    icon_description_embedding = icon_description_embeddings[icon_index]

    # create a DataFrame to store the bullet points
    similarity_scores_df = pd.DataFrame(bullet_point_texts, columns=['bullet_point'])
    

    for i, bp_embedding in enumerate(bullet_point_embeddings):
        # calculate cosine similarity between the bullet point embedding and the average of the use case embeddings for the icon
        use_case_cosine_similarity = cosine_similarity(use_case_mean_embedding, bp_embedding)

        # calculate cosine similarity between the bullet point embedding and the icon description embedding
        icon_description_cosine_similarity = cosine_similarity(icon_description_embedding, bp_embedding)

        similarity_scores_df.at[i, 'use_case_similarity'] = use_case_cosine_similarity
        similarity_scores_df.at[i, 'icon_description_similarity'] = icon_description_cosine_similarity
        
    # Normalize the values for each metric to the range of -1 to 1
    normalized_df = similarity_scores_df[['use_case_similarity', 'icon_description_similarity']].apply(lambda x: (x - x.min()) / (x.max() - x.min()) * (2 - 1e-10) - 1 + 5e-11)    

    # print the normalized DataFrame
    # print(normalized_df)
    
    # calculate the mean scores
    similarity_scores_df['mean_score'] = normalized_df.mean(axis=1) 
        
    # sort the DataFrame by the mean score in descending order
    similarity_scores_df = similarity_scores_df.sort_values('icon_description_similarity', ascending=False)

    # print(f"Bullet points ordered by similarity to icon {icon_original_label}:")
    
    # print(similarity_scores_df)
    
    # return the index with the highest mean score
    return similarity_scores_df.index[0]

# function to get embeddings for a list of bullet points
async def get_embeddings(bps):
    """
    Get embeddings for the given bps.

    Parameters:
    bps (list): A list of bullet points.

    Returns:
    np.array: An array of embeddings.
    """
    return np.array(await openai_embeddings.aembed_documents(bps))

async def get_unique_embeddings(embeddings, threshold=1):
    """
    Given a list of embeddings, calculates a list of embeddings containing the unique information from each embedding amongst the other embeddings. 

    Parameters:
    embeddings (numpy.ndarray): The input embeddings.
    threshold (float): The threshold value for calculating unique embeddings. Default is 1. Higher values will result in more unique embeddings.

    Returns:
    numpy.ndarray: The unique embeddings.
    """
    unique_embeddings = []
     
    for i in range(len(embeddings)):
        current_fact = embeddings[i]
        other_facts = np.delete(embeddings, i, axis=0)
        
        # Calculate the average of all other fact vectors
        other_facts_avg = np.mean(other_facts, axis=0)
        
        # Subtract the weighted average of other facts from the current fact
        unique_fact = current_fact - threshold * other_facts_avg
        
        unique_embeddings.append(unique_fact)
    
    # Convert list to numpy array
    return np.array(unique_embeddings)

# function to get the most similar icon to a bullet point
async def get_most_similar_icon(embedding):
    """
    Returns the most similar icon label based on the given embedding.
    
    Parameters:
        embedding (numpy.ndarray): The embedding representing the icon.
        
    Returns:
        tuple: A tuple containing the original_label and source of the most similar icon.
    """
    result = await choose_icons_from_embedding(embedding)
    return result.iloc[0]['original_label'], result.iloc[0]['source']

async def subtract_vectors(vector1, vector2, threshold=1.0):
    """
    Subtract two vectors with an optional threshold.

    Args:
        vector1 (np.ndarray): The first vector.
        vector2 (np.ndarray): The second vector.
        threshold (float, optional): The threshold value to multiply vector2 by before subtracting from vector1. Defaults to 1.0.

    Returns:
        np.ndarray: The resulting vector after subtraction.
    """
    return vector1 - threshold * vector2

async def get_most_similar_bp_index(bullet_points, embedding, icon):
    """
    Returns the index of the most similar bullet point to the given icon.

    Parameters:
    embedding (np.ndarray): The embedding of the bullet point.
    icon (string): The original_label of the icon to compare with the blueprints.

    Returns:
    int: The index of the most similar bullet point.
    """
    assert type(icon) == str, "icon must be a string"
    assert type(embedding) == np.ndarray, "embedding must be a numpy.ndarray"
    return await get_most_similar_bp_to_icon(bullet_points, embedding, icon)

async def recursive_matching(embeddings, icon, assigned_icons, bullet_points, threshold):
    """Recursively matches bullet points to the most similar icons using unique embeddings.

    Args:
        embeddings (list): List of embeddings for the bullet points.
        icon (tuple): A tuple containing the icon label and source.
        assigned_icons (dict): Dictionary to store the assigned icons.
        bullet_points (list): List of bullet point texts.
        threshold (float): The threshold value for calculating unique embeddings.

    Returns:
        None
    """
    if len(embeddings) == 0:
        # print("No more bullet points to match.")
        return
    
    if len(embeddings) == 1:
        assigned_icons[bullet_points[0]] = icon
        # print(f"Assigned {icon[0]} (Source: {icon[1]}) to `{bullet_points[0]}`. (Group of 1)")
        return
    
    # print(f"Icon `{icon[0]}` (Source: {icon[1]}) matched to {len(embeddings)} bullet points. Breaking down group...")
    
    unique_embeddings = await get_unique_embeddings(embeddings, threshold=0.5)
    max_bullet_point_index = await get_most_similar_bp_index(bullet_points, unique_embeddings, icon[0])
    max_bullet_point = bullet_points[max_bullet_point_index]
    assigned_icons[max_bullet_point] = icon
    # print(f"Assigned {icon[0]} (Source: {icon[1]}) to `{max_bullet_point}` by unique embedding matching.")
    
    remaining_embeddings = [emb for i, emb in enumerate(embeddings) if i != max_bullet_point_index]
    remaining_bullet_points = [bp for i, bp in enumerate(bullet_points) if i != max_bullet_point_index]
    # print(f"Remaining bullet points: {remaining_bullet_points}")
    for embedding, bullet_point in zip(remaining_embeddings, remaining_bullet_points):
        updated_embedding = await subtract_vectors(embedding, embeddings[max_bullet_point_index], threshold=threshold)
        # print(f"Subtracted `{max_bullet_point}` from embedding for `{bullet_point}`.")
        most_similar_icon = await get_most_similar_icon(updated_embedding)
        await recursive_matching([updated_embedding], most_similar_icon, assigned_icons, [bullet_point], threshold=threshold)

async def hybrid_icon_assignment(bullet_points, initial_threshold=0.0, recursive_threshold=1.0):
    """Assign icons to bullet points using a combination of simple similarity matching and recursive unique embedding matching.

    Args:
        bullet_points (list): List of bullet point texts.
        initial_threshold (float): The threshold value for initial unique embeddings calculation. Default is 0.0.
        recursive_threshold (float): The threshold value for recursive unique embeddings calculation. Default is 1.0.

    Returns:
        dict: Dictionary with bullet points as keys and assigned icons as values.
    """
    assigned_icons = {}
    
    # Step 1: Simple Similarity Matching
    icon_groups = {}
    simple_embeddings = await get_embeddings(bullet_points)
    if initial_threshold == 0:
        adjusted_embeddings = simple_embeddings
    else:
        adjusted_embeddings = await get_unique_embeddings(simple_embeddings, threshold=initial_threshold)
    for i, embedding in enumerate(adjusted_embeddings):
        icon_label, icon_source = await get_most_similar_icon(embedding)
        if icon_label not in icon_groups:
            icon_groups[icon_label] = []
        icon_groups[icon_label].append((bullet_points[i], embedding, icon_source))
    
    # Step 2: Unique Embedding Matching
    for icon_label, group in icon_groups.items():
        bullet_points_group = [item[0] for item in group]
        embeddings_group = [item[1] for item in group]
        icon_source = group[0][2]  # Use the source from the first item in the group
        icon = (icon_label, icon_source)
        await recursive_matching(embeddings_group, icon, assigned_icons, bullet_points_group, threshold=recursive_threshold)
    
    return assigned_icons

# FOR API

async def get_top_n_icons_for_bullet_point(bullet_point, n):
    """Returns the top n icons for a given bullet point based on similarity.

    Args:
        bullet_point (str): The bullet point in question.
        n (int): The number of top similar icons to return.

    Returns:
        list: A list of n icon objects in descending order of similarity.
    """
    query_embedding = np.array(await openai_embeddings.aembed_query(bullet_point))
    similarity_df = await similarity_search(query_embedding, grouped_use_case_embeddings, icon_description_embeddings)
    top_n_icons = similarity_df.head(n).to_dict(orient='records')
    
    # Convert to the required icon object format
    icon_objects = [{'icon_name': icon['icon_name'], 'original_label': icon['original_label'], 'source': icon['source']} for icon in top_n_icons]
    
    return icon_objects


async def get_top_n_icons_with_unique_embedding(bullet_point, bullet_point_list, n):
    """Returns the top n icons for a given bullet point after subtracting the average embeddings of other bullet points.

    Args:
        bullet_point (str): The bullet point in question.
        bullet_point_list (list): List of bullet points including the bullet point in question.
        n (int): The number of top similar icons to return.

    Returns:
        list: A list of n icon objects in descending order of similarity.
    """
    if bullet_point not in bullet_point_list:
        raise ValueError("The bullet point in question must be in the provided bullet point list.")
    
    bullet_point_index = bullet_point_list.index(bullet_point)
    bullet_point_embeddings = await get_embeddings(bullet_point_list)
    unique_embeddings = await get_unique_embeddings(bullet_point_embeddings)
    
    query_embedding = unique_embeddings[bullet_point_index]
    similarity_df = await similarity_search(query_embedding, grouped_use_case_embeddings, icon_description_embeddings)
    top_n_icons = similarity_df.head(n).to_dict(orient='records')
    
    # Convert to the required icon object format
    icon_objects = [{'icon_name': icon['icon_name'], 'original_label': icon['original_label'], 'source': icon['source']} for icon in top_n_icons]
    
    return icon_objects


async def get_top_n_icons_for_query(query, n):
    """Returns the top n icons for a given search query based on similarity to icon descriptions.

    Args:
        query (str): The search query.
        n (int): The number of top similar icons to return.

    Returns:
        list: A list of n icon objects in descending order of similarity.
    """
    query_embedding = np.array(await openai_embeddings.aembed_query(query))
    
    # Modify similarity_search function to exclude use case similarity
    def similarity_search_icon_descriptions_only(query_embedding, icon_description_embeddings):
        df = pd.DataFrame(valid_data)
        
        # Compute cosine similarity between the query embedding and the icon description embeddings
        cosine_similarities_icon_descriptions = [cosine_similarity(query_embedding, embedding) for embedding in icon_description_embeddings]
        
        df['icon_description_cosine_similarity'] = cosine_similarities_icon_descriptions
        
        # Sort by icon description similarity
        df = df.sort_values('icon_description_cosine_similarity', ascending=False)
        
        # Reindex the dataframe
        df = df.reset_index(drop=True)
        
        return df
    
    similarity_df = similarity_search_icon_descriptions_only(query_embedding, icon_description_embeddings)
    top_n_icons = similarity_df.head(n).to_dict(orient='records')
    
    # Convert to the required icon object format
    icon_objects = [{'icon_name': icon['icon_name'], 'original_label': icon['original_label'], 'source': icon['source']} for icon in top_n_icons]
    
    return icon_objects
