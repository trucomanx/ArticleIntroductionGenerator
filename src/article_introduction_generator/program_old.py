import os

import article_introduction_generator.about as about
import article_introduction_generator.modules.configure as configure 

# Caminho para o arquivo de configuração
CONFIG_PATH = os.path.join(os.path.expanduser("~"),".config",about.__package__,"config.json")

configure.verify_default_config(CONFIG_PATH, default_content={"casa":"verde"})

CONFIG=configure.load_config(CONFIG_PATH)
print("Hola!")
