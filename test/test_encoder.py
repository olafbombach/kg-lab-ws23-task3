from source.Encoder import Encoder

test_dict = {'full_title': 'Test conference in Germany', 'country': 'Germany', 'city':'Aachen'}

def test_bert_encoding():
    """
    Test the creation of an encoding.
    """
    enc = Encoder(dict_file=test_dict, technique='bert')
    vec = enc.get_bert_encoding(full_title=True)

    assert len(vec) > 100, "In general the BERT encoding is assumed to have higher dimensions."


# unfortunately, we cannot test the glove encoding since this requires the download of the glove resource

