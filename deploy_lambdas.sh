#!/bin/bash
set -e

ZIP=function.zip
rm -f $ZIP

# Package code
zip -r $ZIP handlers/ services/ utils/ config.py

# Upload handler
aws --endpoint-url=$ENDPOINT lambda create-function \
  --function-name UploadImage \
  --runtime $LAMBDA_RUNTIME \
  --role $LAMBDA_ROLE \
  --handler handlers/upload_handler.lambda_handler \
  --zip-file fileb://$ZIP || \
aws --endpoint-url=$ENDPOINT lambda update-function-code \
  --function-name UploadImage \
  --zip-file fileb://$ZIP
