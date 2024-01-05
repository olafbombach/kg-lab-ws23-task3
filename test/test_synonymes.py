from source.synonymes import Synonymes



def test_synonymes_method():
    results = "['2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25 Aug. 2023', '2023 3rd International Conference on Information    Management and Technology (ICIMTech) 24-25 Aug. 2023']"
    assert (Synonymes.synonymes("2023 Third International Conference on Information Management and Technology (ICIMTech) 24-25 Aug. 2023") == results)
