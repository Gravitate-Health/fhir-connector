import sys
import os

sys.path.append("..")
sys.path.append("./assets")
import providers.sushi_provider


""" def test_execute_sushi():
    sushi_provider = providers.sushi_provider.sushiProvider()
    fsh_path = "./assets/fsh"
    generated_fsh_path = f"{fsh_path}/fsh-generated/resources/"
    sushi_provider.execute_sushi(fsh_path)
    assert os.listdir(generated_fsh_path).__len__ != 0
 """