import sys
import os
import json

sys.path.append("./assets")
sys.path.append("../providers")

import providers.fhir_provider

def test_separate_bundle():
    fhir_provider = providers.fhir_provider.FhirProvider()
    print(os.listdir("./"))
    bundle = json.load(open("./src/tests/test_files/bundle.json"))
    separated_bundle = fhir_provider.separate_bundle_into_resources(bundle)
    assert separated_bundle.__len__ != 0


test_separate_bundle()
