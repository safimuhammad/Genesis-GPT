def format_filename(file_path):
    """Extracts filename from file path"""
    split_path= file_path.split('/')
    return split_path[-1]

# def format_abilities(abilities):
#     assert isinstance(abilities,dict) , "cannot format abilities JSON"
#     formatted_ab=[]
#     for i in abilities['abilities']:

