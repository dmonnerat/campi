#aws s3 cp $1 s3://kettlepotcampi > output
aws rekognition list-faces --collection-id "friends" \
--image "{\"S3Object\":{\"Bucket\":\"kettlepotcampi\",\"Name\":\"$1\"}}" \
--region us-east-1 
