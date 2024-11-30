from elasticsearch import Elasticsearch

#to adjust later using .env and setting conf
es = Elasticsearch('https://localhost:9201', basic_auth=('elastic', 'adminadmin'), ca_certs="dbs/elastic/certs/ca/ca.crt")
print(es.info(pretty=True))
