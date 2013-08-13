$.widget("custom.catcomplete", $.ui.autocomplete, {
	_renderMenu: function( ul, items) {
		var that = this, currentCategory = "";
		$.each(items, function(index, item) {
			if (item.category != currentCategory) {
				ul.append("<li class='ui-autocomplete-category'>" + item.category + "<\li>");
				currentCategory = item.category;
			}
			that._renderItemData(ul, item);
		});
	}
});
$(function() {
	$.ajax({
		url : '/test',
		dataType: 'html',
		type : 'GET',
		success: function(data) {
			var splitData = [];
			var categories = data.split("*");
			for (var i = 0, len = categories.length, options; i < len; i++) {
				options = categories[i].split("\n");
				splitData[i] = options
			}
			splitData.push(["Distribution Areas", "EC", "EM", "HA", "LA", "QR", "SA", "STL", "STN"])
			//alert("done")
			$(".autosearch").catcomplete({
				delay: 0,
				source: function(request, response) {
					var n = 0
					var term = request.term
					var res = []
					var isQuote = new RegExp("^\".+\"", "i");
					var isMore = new RegExp("^\".+\" in [a-z]+", "i");
					var isIn = new RegExp("^\".+\" in?", "i");
					var isDis = new RegExp("^\".+\" [a-z]{1,2}", "i");
					if (isQuote.test(term) == true) {
						if (isIn.test(term) == true) {
							if (isMore.test(term) == true) {
								var cut = isIn.exec(term)
								var text = term.substr(term.indexOf(" in ")+4)
								var matcher = new RegExp(text, "i")
								for (var i = 0, len = splitData.length; i < len; i++) {
									var cat = splitData[i][0]
									if (cat === "Courses" || cat === "Professors")
										continue

									for (var j = 1, len2 = splitData[i].length,  max=2, count=0; j < len2 && count <= max; j++) {
										var lab = splitData[i][j]
										if (matcher.test(lab) == true) {
											res[n] = {}
											res[n].label = cut + " " + lab;
											res[n].category = splitData[i][0]
											n++;
											count++;
										}
									}
								}
							}
						}
					}
						if (!isMore.test(term) && (term.lastIndexOf("\"")==0 || isQuote.test(term) || isIn.test(term))) {
							var append = ""
							var match = true
							if (term.lastIndexOf("\"")==0) {
								append = "...\" in "
							} else if (term.search(/\"$/g) != -1) {
								append = " in "
							} else if (term.search(/\"\s$/) != -1) {
								append = "in "
							} else if (term.search(/i$/) != -1) {
								append = "n "
							} else if (term.search(/n$/) != -1) {
								append = " "
							} else if (term.search(/\s$/) == -1) {
								match = false
							}
							if (match) {
							for (var i =0, len = splitData.length; i < len; i++) {
								var cat = splitData[i][0]
								if (cat === "Courses" || cat === "Professors")
									continue
								res[n] = {};
								res[n].label = term + append + "..."
								res[n].category = cat
								n++;
							}}
						}
					//}
					var matcher = new RegExp($.ui.autocomplete.escapeRegex( request.term ), "i" );
					for (var i = 0, len = splitData.length; i < len; i++) {
						var cat = splitData[i][0];
						if (cat === "Distribution Areas") {
							continue
						}
						for (var j = 1, len2 = splitData[i].length, max=2, count=0; j < len2 && count <= max; j++) {
							var lab = splitData[i][j];
							if (matcher.test(lab) == true) {
								res[n] = {};
								res[n].label = lab;
								res[n].category = cat;
								n++;
								count++;
							}
						}
					}
					response(res);
				},
				select: function(event, ui) {
					//check if course
					var t = ui.item.value
					var cpatt = new RegExp("^[A-Z]{3}\\s[0-9]+", "i")
					var dmpatt = new RegExp("^[A-Z]{3}:", "i")
					var dpatt = new RegExp("^[A-Z]{3}", "i")
					if (cpatt.test(t) == true) {
						var cnd = dpatt.exec(t)
						var cnnpatt = new RegExp("[0-9]+[a-z]*", "i")
						var cnn = cnnpatt.exec(t)
						window.location = "http://easypce.com/courses/" + cnd + cnn
					}
					else if (dmpatt.test(t) == true) {
						d = dpatt.exec(t)
						window.location = "http://easypce.com/depts/" + d
					}
					else if (t.search(/".+" in [a-z]+/i) != -1) {
						var q = t.match(/".+" in [a-z]+:?/i)[0]
						if (q.search(/:$/) != -1) {
							q = q.match(/".+" in [a-z]+/i)[0]
						}
						q.replace(/\s/g, "+")
						window.location = "http://easypce.com/search/?q=" + q
					} else {
						p = t.replace(/\s/g, "+")
						window.location = "http://easypce.com/search/?q=" + p
					}
				}
			});
		}
	});	
});
