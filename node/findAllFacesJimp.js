var AWS = require('aws-sdk');
AWS.config.update({region:'us-east-1'});

var easyimg = require('easyimage');
var Jimp = require("jimp");
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

rekognition.detectFaces(params, function (err, data) {
  if (err) console.log(err, err.stack); // an error occurred
  else
  {
    // successful response
    //console.log(JSON.stringify(data, null, '\t'));
    //console.log(data.FaceDetails.length);
    data.FaceDetails.forEach(function(face) {

//    for(var face of data.FaceDetails){
//      iter++;
//    for(var iter=0; iter<data.FaceDetails.length; iter++)
//    {

//      var top = data.FaceDetails[iter].BoundingBox.Top;
//      var left = data.FaceDetails[iter].BoundingBox.Left;
//      var height = data.FaceDetails[iter].BoundingBox.Height;
//      var width = data.FaceDetails[iter].BoundingBox.Width;

      var top = face.BoundingBox.Top;
      var left = face.BoundingBox.Left;
      var height = face.BoundingBox.Height;
      var width = face.BoundingBox.Width;

      console.log(JSON.stringify(face.BoundingBox, null, '\t'));

      /*
      Face #1
      {
              "Width": 0.23777778446674347,   = 835.31335683166981011
              "Height": 0.3566666543483734, = 835.3133044838905028
              "Left": 0.2522222101688385, 886.0566243231296505
              "Top": 0.09666666388511658 =226.39332681894303036
      }

      Face #2
      {
              "Width": 0.20444443821907043, = 718.2133114635943152
              "Height": 0.30666667222976685, = 718.2133463621139627
              "Left": 0.4699999988079071, = 1651.1099958121776423
              "Top": 0.21833333373069763 = 511.33666759729384946
      }


/*
width: 3513,
height: 2342,
*/
    var imgWidth = 3857;
    var imgHeight = 2571;

/*
    easyimg.crop(
      {src:'dave/davekerri1.jpg',dst:'dave/out' + iter + '.jpg',
          x:(left*imgWidth), y:(top*imgHeight), cropwidth:((left*imgWidth)+(width*imgWidth)), cropheight:((top*imgHeight)+(height*imgHeight))}
        ).then(
      function(image) {
         console.log('x: ' + (left*imgWidth) + ' y: ' + (top*imgHeight) + ' width: ' + ((left*imgWidth)+(width*imgWidth)) + ' height: ' + ((top*imgHeight)+(height*imgHeight)));
         //console.log('Resized and cropped: ' + image.width + ' x ' + image.height);
      },
      function (err) {
        console.log(err);
      }
    );
*/
    Jimp.read("dave/" + testImage).then(function (image) {
        // do stuff with the image
        image.clone();
        image.crop( (left*imgWidth), (top*imgHeight), ((width*imgWidth)), ((height*imgHeight)) );         // crop to the given region
        //var file = "dave/new_name " + new Date().getUTCMilliseconds() + "." + image.getExtension();
        //image.write(file)
        //console.log("Wrote " + file);

        image.getBuffer( Jimp.AUTO, function (err, bufData)
{

  var imageBytes = getBinary(bufData);

         var imgParams = {
          Image: {
           Bytes: imageBytes
         },
         CollectionId: "friends"
        };


        console.log("Image bytes: " + imageBytes);

         rekognition.searchFacesByImage(imgParams, function (err, data) {
           if (err) console.log(err, err.stack); // an error occurred
           else
           {
             console.log(JSON.stringify(data, null, '\t'));
           }
         }
         );


}



       );




    }).catch(function (err) {
        // handle an exception
        console.log("there was a problem " + err);
    });

  })

//    } //end for loop
   }
});


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
