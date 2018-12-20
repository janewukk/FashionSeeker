function parseJwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse(window.atob(base64));
};

function extractHostname(url) {
	var hostname;
	//find & remove protocol (http, ftp, etc.) and get hostname
	if (url.indexOf("://") > -1)  {
		hostname = url.split('/')[2];
	}
	else  {
		hostname = url.split('/')[0];
	}
	//find & remove port number
	hostname = hostname.split(':')[0];
	//find & remove "?"
	hostname = hostname.split('?')[0];
	return hostname;
}

function createCORSRequest(method, url, id) {
	var xhr = new XMLHttpRequest;
	try {
		xhr.onreadystatechange = function() {
			if (xhr.readyState === 4)  {
				if(xhr.status === 200) 
				{
					document.getElementById(id).setAttribute("src",  url);
				}
			}
		}
		xhr.open(method, url);
		xhr.send();
	}
	catch(e) {
		throw e;
	}
}

function extractRootDomain(url) {
	var domain = extractHostname(url),
		splitArr = domain.split('.'),
		arrLen = splitArr.length;

	if(splitArr[0] === "www") {
		domain = domain.substring(4, domain.length);
	}
	return domain;
}
$(window).load(function() 
{
   // executes when complete page is fully loaded, includinalert("(window).load was called - window is loaded!");
});  

var keyList = {};
var count = 0;

$(document).ready(function(){
	console.log("loggedin");
	var cur_email;
	if (window.location.href.indexOf("id_token") >= 0) {
		var urlParams = new URLSearchParams(window.location.href.split("#")[1]);
		var id_token = urlParams.get("id_token");
		var cur_user = parseJwt(id_token);
		console.log(cur_user);
		cur_email = cur_user["email"];
		console.log(cur_email);
	}
	else {
		window.location.href = "https://fashion.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=6s9ikbtlbk378tpga5v1msh2o6&redirect_uri=https://s3.amazonaws.com/fashionseeker/index.html";
	}
	// show my discount when loggedin

	// POST: input + email, searching
	$("#search_button").click(function(){
		var input = $('#search_query').val();
		var q = input + "+" + cur_email;

		var apigClient = apigClientFactory.newClient();
		var params = {
		};
		var body = {
			"q": q
		};

		apigClient.rootPost(null, body)
		.then(function(result){
			console.log("fashionApiPost");
			console.log(result)
			var info = $.parseJSON(result.data.body);
			
			if(info["results"]["Item"] != undefined)
			{

				var url = info["results"]["Item"]["url"];
				var name = info["results"]["Item"]["name"];
				var discount = info["results"]["Item"]["discount"];
				var discount_array = JSON.parse(discount);
				if(keyList[name] != undefined )
				{
					alert("The website you searched has already listed here")
				}
				else
				{
					keyList[name] = true;
					console.log(info);
					var discount_content = "";
					for(i = 0; i < discount_array.length; i++){
						discount_content += '<p class="text-content">' + discount_array[i] + '</p>';
					}
					$('#search_result').prepend('<div class="row mb-3 mt-3 align-items-center bg-white rounded shadow-sm">\
													<div class="col-12 col-md-3 "><img width="80%" id="'+url+'" src="logo.png"></div>\
													<div class="col-12 col-md-8">\
														<h3>' + name + '</h3>' + discount_content + '\
														<div class="row justify-content-end">\
																<div class="col-sm-4">\
															    	<a class="btn btn-success my-3 btn-block" href="'+url+'">View</a>\
																</div>\
														</div>\
													</div>\
												</div>');

					createCORSRequest('GET', "https://logo.clearbit.com/" + extractRootDomain(url), url);
				}				
			}
			else
			{
				alert("The website you searched was not found.")
			}
		
		})
		.catch(function(result) {
			console.log(result);
		});
	});

	// GET: input, show discount
	$("#discount_button").click(function(){
		console.log("test");
		if(count != 0)
			return;
		count++;
		var apigClient = apigClientFactory.newClient();
		var params = {
			"q": cur_email,
			"mode": "1"
		};
		var body = {
			
		}
		console.log(params)

		apigClient.rootGet(params)
		.then(function(result){
			console.log("fashionApiGet");
			// console.log(JSON.parse(result.data))
			// console.log(result)
			var data = JSON.stringify(result.data)
			data = JSON.parse(data)
			var info = data["results"]
			var keysOfInfo = Object.keys(info)
			for(var j = 0; j < keysOfInfo.length; ++j)
			{
				var name = keysOfInfo[j];
				var discount_array = info[keysOfInfo[j]]
				var url = info[keysOfInfo[j]][0]
				if(keyList[name] != undefined )
				{
					alert("The website you searched has already listed here")
				}
				else
				{
					keyList[name] = true;
					console.log(info);
					var discount_content = "";
					for(i = 1; i < discount_array.length; i++){
						discount_content += '<p class="text-content">' + discount_array[i] + '</p>';
					}
					$('#search_result').append('<div class="row mb-3 mt-3 align-items-center bg-white rounded shadow-sm">\
													<div class="col-12 col-md-3 "><img width="80%" id="'+name+'" src="logo.png"></div>\
													<div class="col-12 col-md-8">\
														<h3>' + name + '</h3>' + discount_content + '\
														<div class="row justify-content-end">\
																<div class="col-sm-4">\
															    	<a class="btn btn-success my-3 btn-block" href="'+url+'">View</a>\
																</div>\
														</div>\
													</div>\
												</div>');

					createCORSRequest('GET', "https://logo.clearbit.com/" + extractRootDomain(url), name);
				}
			}
		})
		.catch(function(result) {
			console.log("catch");
			console.log(result);
		});
	});
	$("#send_email").click(function(){
		console.log("test send email");
		var apigClient = apigClientFactory.newClient();
		var params = {
			"q": cur_email,
			"mode": "2"
		};
		var body = {
			
		}
		console.log(params)

		apigClient.rootGet(params)
		.then(function(result){
			console.log("sent email!!!");
		})
		.catch(function(result) {
			console.log("catch email exception");
			console.log(result);
		});
	});

});





