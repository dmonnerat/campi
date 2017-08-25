import boto3

s3 = boto3.resource('s3')
rek = boto3.client('rekognition') # Setup Rekognition

# Get list of objects for indexing
#images=[('dave.jpg','David_Monnerat'),
#      ('dave2.png','David_Monnerat'),
#      ('dave3.png','David_Monnerat'),
#      ('dave4.jpg','David_Monnerat'),
#      ('dave5.jpg','David_Monnerat'),
#      ('mitchell1.jpg','Mitchell_Monnerat'),
#      ('face3.jpg','Kerri_Monnerat'),
#      ('kerri1.jpg','Kerri_Monnerat'),
#      ('kerri2.jpg','Kerri_Monnerat'),
#      ('hawaii-2017-makapuu-6559.jpg','Mitchell_Monnerat'),
#      ('mom.jpg','Kathy_King'),
#      ]

images=[('kerri10.jpg','Kerri_Monnerat'),
      ('kerri11.jpg','Kerri_Monnerat'),
      ('kerri12.jpg','Kerri_Monnerat'),
      ('kerri13.jpg','Kerri_Monnerat')
      ]

# Iterate through list to upload objects to S3
for image in images:
    file = open(image[0],'rb')
    object = s3.Object('campi-rekognition-pictures','index/'+ image[0])
    ret = object.put(Body=file,
                    Metadata={'FullName':image[1]}
                    )


    faceResults = rek.index_faces(
        Image={
            'S3Object': {'Bucket': 'campi-rekognition-pictures', 'Name': 'index/' + image[0]}
        },
        CollectionId="family_collection",
        DetectionAttributes=["ALL"],
        ExternalImageId=image[1]
    )
