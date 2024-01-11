from source.synonymes import Synonymes



def test_synonymes_method():
    results = {'2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25 Aug. 2023': 4, '2023 3rd International Conference on Information Management and Technology (ICIMTech) 24-25 Aug. 2023': 3, '2023': 1, '24-25': 1, 'ICIMTech': 3, '24:08:2023': 2, '2023 Third': 1, '2023 Third International': 1, '2023 Third International Conference': 1, '2023 Third International Conference on': 1, '2023 Third International Conference on Information': 1, '2023 Third International Conference on Information Management': 1, '2023 Third International Conference on Information Management and': 1, '2023 Third International Conference on Information Management and Technology': 1, '2023 Third International Conference on Information Management and Technology (ICIMTech)': 1, '2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25': 1, '2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25 Aug.': 1}
    assert (Synonymes.synonymes("2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25 Aug. 2023").keys() == results.keys())
