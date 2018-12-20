XMLHttpRequest = require("xhr2")
// TODO implement

exports.handler = (event, context, callback) => {
	var response = {};
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
	
	function find_next_index(content, start_index) {
		var idx = content.indexOf("% off", start_index);
		var capital_idx = content.indexOf("% Off", start_index);
		var cap_2_idx = content.indexOf("% OFF", start_index);
		if(capital_idx !== -1) {
			if(idx === -1 || (capital_idx < idx)) {
				idx = capital_idx;
			}
		}
		if(cap_2_idx !== -1) {
			if(idx === -1 || (cap_2_idx < idx)) {
				idx = cap_2_idx;
			}
		}
		return idx;
	}
	
	var performSomeAction = function(returned_data) {
		console.log("callback function called");
	    console.log(returned_data);
	    callback(null, {
            statusCode: 200,
            body: JSON.stringify(returned_data)
        });
	};
	
	var all_discout = [];
	function extract_all_discout(method, url, callback1) {
		var xhr = new XMLHttpRequest;
		// var all_discout = [];
		var discount_num_st = new Set();
		try {
			xhr.onreadystatechange = function() {
				if (xhr.readyState === 4) {
					if(xhr.status === 200) {
						var content = xhr.response;
						var idx = find_next_index(content, 0);
						
						if(idx === -1) {
							all_discout.push("No discount information found");
						}
						else {
							while (idx !== -1) {
								var cur_start = idx;
								while(content[cur_start] !== '"' && content[cur_start] !== " " && content[cur_start] !== ">")  {
									cur_start -= 1;
								}
								var discount_num = Number(content.substring(cur_start+1, idx));
	
								if (!discount_num_st.has(discount_num)) {
									discount_num_st.add(discount_num);
									var start_idx = idx;
									var end_idx = idx+5;
									// for full text
									while(content[start_idx] !== ">" && content[start_idx] !== '"' && content[start_idx] !== "-") {
										start_idx -= 1;
									}
									while(content[end_idx] !== "<" && content[end_idx] !== '"' && content[end_idx] !== "." 
										&& content[end_idx] !== "!" && content[end_idx] !== "-") {
										end_idx += 1;
									}
									// var discountSentence = "";
									// discountSentence += content.substring(start_idx+1, end_idx);
									all_discout.push(content.substring(start_idx+1, end_idx));
								}
								idx = find_next_index(content, idx + 5);
							}
							
						}
						var tempResponse = (all_discout);
					    callback1(tempResponse);
					}
				}
			};
			xhr.open(method, url);
			xhr.send();
		}
		catch(e) {
			throw e;
		}
	}
	try{
		extract_all_discout("GET", event, performSomeAction);
	}
	catch(e)
	{
		console.log("incorrect");
	}
};
