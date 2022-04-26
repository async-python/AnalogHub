#!/bin/bash

status_code_analog=$(curl --write-out %\{http_code\} --silent --output -XGET -H 'Content-Type:application/json' "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_ANALOG}")
status_code_product=$(curl --write-out %\{http_code\} --silent --output -XGET -H 'Content-Type:application/json' "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_PRODUCT}")

if [ "$status_code_analog" -ne 200 ]
then
  curl -XPUT -H 'Content-Type:application/json' --data-binary "@/home/curl_user/schemas_row.json" "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_ANALOG}"
else
  echo "scheme ${ELASTIC_INDEX_ANALOG} exists, status: ${status_code_analog}"
fi

if [ "$status_code_product" -ne 200 ]
then
  curl -XPUT -H 'Content-Type:application/json' --data-binary "@/home/curl_user/scheme_product.json" "${ELASTIC_HOST}":"${ELASTIC_PORT}"/"${ELASTIC_INDEX_PRODUCT}"
else
  echo "scheme ${ELASTIC_INDEX_PRODUCT} exists, status: ${status_code_product}"
fi

exit 0