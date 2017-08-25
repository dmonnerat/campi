var AWS = require('aws-sdk');
AWS.config.update({region:'us-east-1'});

var sharp = require('sharp');
var async = require('async');

var btoa = require('btoa');
var atob = require('atob');

var rekognition = new AWS.Rekognition();

var testImage = "hawaii-2017-luau-6312.jpg";

var params = {
 Image: {
  S3Object: {
   Bucket: "kettlepotcampi",
   Name: testImage
  }
 }
};

var data;
var iter = 0;

var knownFaces = 0;
var unknownFaces = 0;

rekognition.detectFaces(params, function (err, data) {
  if (err)
  {
    // an error occurred
    console.log(err, err.stack);
  }
  else
  {
    // successful response
    //console.log(JSON.stringify(data, null, '\t'));
    //console.log(data.FaceDetails.length);
    data.FaceDetails.forEach(function(face) {

      var imgWidth = 3857;
      var imgHeight = 2571;

      var top = Math.floor(face.BoundingBox.Top * imgHeight);
      var left = Math.floor(face.BoundingBox.Left * imgWidth);
      var height = Math.ceil(face.BoundingBox.Height * imgHeight);
      var width = Math.ceil(face.BoundingBox.Width * imgWidth);

      console.log(JSON.stringify(face.BoundingBox, null, '\t'));

      sharp("dave/" + testImage)
        .extract({ left: left, top: top, width: width, height: height })
        .toBuffer(function (err, bufData) {

          var imageBytes = getBinary(bufData);
          lookupFace(imageBytes);

        }); //end sharp extract to buffer

    }); //end forEach face function

    console.log("  Known faces: " + knownFaces)
    console.log("Unknown faces: " + unknownFaces)

  } //end I found faces


}); //end detect faces


function getBinary(base64Image) {

   var binaryImg = atob(base64Image);
   var length = binaryImg.length;
   var ab = new ArrayBuffer(length);
   var ua = new Uint8Array(ab);
   for (var i = 0; i < length; i++) {
     ua[i] = binaryImg.charCodeAt(i);
    }

    return ab;
}

function lookupFace(imageBytes) {

  console.log("Image bytes: " + imageBytes);

  var imgParams = {
                     Image: {
                      Bytes: imageBytes
                            },
                    CollectionId: "friends"
                 };

   rekognition.searchFacesByImage(imgParams, function (err, data) {
         if (err)
         {
           console.log("I got back an erro", err, err.stack); // an error occurred
           unknownFaces++;
         }
         else
         {
           console.log(JSON.stringify(data, null, '\t'));
         }
       }); //end searchFacesByImage call
} //end lookupFace
