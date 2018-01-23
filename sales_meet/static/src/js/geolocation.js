odoo.define('sales_meet.currentlatlong', function (require) {
    "use strict";

var instance = openerp;
var core = require('web.core');
var Model = require('web.Model');
var QWeb = core.qweb;
var _t = core._t;
var longitude = 0.0;
var latitude = 0.0;


instance.web.FormView.include({
    init: function(parent, dataset, view_id, options) {
        var self = this;
        this._super(parent, dataset, view_id, options);
    },
    
    start: function() {
        var self = this;
        this._super.apply(this, arguments);
        // console.log("__INIT__" + latitude + longitude);
        // $('input.checkin_lattitude').val(latitude);
        // $('input.checkin_longitude').val(longitude);
        
        this.$el.delegate('.geo_checkin', 'click', this.get_location);



    },
    
    get_location: function(){
        $('input.checkin_lattitude').val(latitude);
        $('input.checkin_longitude').val(longitude);
    },
    
});


var options = {
    enableHighAccuracy: true,
    maximumAge: 3600000
};

function success(pos) {
  var crd = pos.coords;

  console.log('Your current position is:');
  console.log(`Latitude : ${crd.latitude}`);
  console.log(`Longitude: ${crd.longitude}`);
  console.log(`More or less ${crd.accuracy} meters.`);
  
  var checkin_lattitude = crd.latitude;
  var checkin_longitude = crd.longitude;
  longitude = checkin_longitude;
  latitude = checkin_lattitude;
};

function error(err) {
  console.warn(`ERROR(${err.code}): ${err.message}`);
};


// var latLong;
//     $.getJSON("http://ipinfo.io", function(ipinfo){
//         console.log("Found location ["+ipinfo.loc+"] by ipinfo.io");
//         latLong = ipinfo.loc.split(",");
//         console.log("__INIT__" + latLong);


//     });



// function do_something(coords) {
//     // Do something with the coords here
// }

// navigator.geolocation.getCurrentPosition(function(position) { 
//     do_something(position.coords);
//     },
//     function(failure) {
//         $.getJSON('https://ipinfo.io/geo', function(response) { 
//         var loc = response.loc.split(',');
//         var coords = {
//             latitude: loc[0],
//             longitude: loc[1]
//         };
//         do_something(coords);
//         });  
//     };
// });

navigator.geolocation.getCurrentPosition(success, error, options);

});

