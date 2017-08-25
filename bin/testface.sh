#aws s3 cp $1 s3://kettlepotcampi > output
aws rekognition search-faces-by-image --collection-id "friends" \
--image "{\"S3Object\":{\"Bucket\":\"kettlepotcampi\",\"Name\":\"$1\"}}" \
--region us-east-1 \
--max-faces 100
