from typing import Dict


class IdInfo:

    def __init__(self, id_info_data: Dict):
        self.iss: str = id_info_data.get('iss')
        self.sub: str = id_info_data.get('sub')
        self.aud: str = id_info_data.get('aud')
        self.iat: int = id_info_data.get('iat')
        self.exp: int = id_info_data.get('iat')
