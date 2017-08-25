aws s3 cp $1 s3://kettlepotcampi > output
aws rekognition index-faces \
  --image "{\"S3Object\":{\"Bucket\":\"kettlepotcampi\",\"Name\":\"$1\"}}" \
--collection-id "friends" --detection-attributes "ALL" \
--external-image-id "$2" \
--region us-east-1
