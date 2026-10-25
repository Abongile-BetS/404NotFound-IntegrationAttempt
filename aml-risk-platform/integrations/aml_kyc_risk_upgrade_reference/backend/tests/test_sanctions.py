from app.services.sanctions import parse_un_xml


def test_fic_xml_is_parsed_with_reference_alias_and_identity_fields():
    content = b"""<NewDataSet><Table><IndividualID>1</IndividualID><ReferenceNumber>QDi.001</ReferenceNumber><FullName>Example Person</FullName><IndividualAlias>Example Alias</IndividualAlias><IndividualDateOfBirth>1970-01-01</IndividualDateOfBirth><Nationality>Exampleland</Nationality><ListedOn>2001-01-01</ListedOn></Table></NewDataSet>"""
    records = parse_un_xml(content, "FIC", "https://example.test")
    assert len(records) == 1
    assert records[0].reference == "QDi.001"
    assert records[0].aliases == ["Example Alias"]
    assert records[0].record_type == "individual"
