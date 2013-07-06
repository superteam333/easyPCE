$(function() {
    // get data from server
    var splitData = [];
    splitData.push(["Distribution Areas", "EC", "EM", "HA", "LA", "QR", "SA", "STL", "STN"]);
    $.ajax({
        url : '/test',
        dataType: 'html',
        type : 'GET',
        success: function(data) {
            var categories = data.split("*");
            for (var i = 0, len = categories.length; i < len; i++) {
                splitData.push(categories[i].split("\n"));
            }
        }
    });

    $.widget("custom.catcomplete", $.ui.autocomplete, {
        _renderMenu: function(ul, items) {
            var that = this, currentCategory = "";
            $.each(items, function(index, item) {
                if (item.category != currentCategory) {
                    ul.append("<li class='ui-autocomplete-category'>" + item.category + "<\li>");
                    currentCategory = item.category;
                }
                that._renderItemData(ul, item)
            });
        }, _renderItemData: function( ul, item ) {
                return this._renderItem( ul, item ).data( "ui-autocomplete-item", item );
        },

        _renderItem: function( ul, item ) {
                return $( "<li>" )
                .append("<a>"+item.label+"</a>")
                .appendTo( ul );
        }
    });

    function getEmptyList() {
        console.log("empty")
        var res = []
        res.push({label: "Search by course name or number", category: ""})
        res.push({label: "Search by department", category: ""})
        res.push({label: "Search by distribution area", category: ""})
        res.push({label: "Search by "})
        return res
    }

    function getReviewList(term) {
        var res = [];
        var match;
        
        //re = /\sin\s*[a-z]+/i;
        // more if needed

        re = /^.+ in [a-z]+/i;
        if (re.test(term)) {
            match = re.exec(term)[0]
            var after = term.substr(term.indexOf(" in ")+4)
            var bef = term.substr(0, term.indexOf(" in "));
            var afterWords = after.split(" ")
            for (var w = afterWords.length; w >0; w--) {
                var after = afterWords[0]
                for (var wi = 1; wi < w; wi++)
                    after = after + " " + afterWords[wi]

                var matcher = new RegExp(after, "i")
                for (var i = 0, len = splitData.length; i < len; i++) {
                    var cat = splitData[i][0]
                    if (cat === "Courses" || cat === "Professors")
                        continue
                    for (var j = 1, len2 = splitData[i].length,  max=5, count=0; j < len2 && count <= max; j++) {
                        var lab = splitData[i][j]
                        if (matcher.test(lab) == true) {
                            res.push({
                                label: "<b>" + bef + "</b>" + " in " + "<b>" + lab + "</b>",
                                category: "Reviews"
                            })
                            count++;
                        }
                    }
                }
                if (res.length > 0)
                    return {match: match, list: res}
            }
            return {match: match, list: res}
        }
        // should also just have something for aksdjfhk and add in whatever
        var re = /^.+ i($|n\s?)/i;
        if (re.test(term)) {
            match = re.exec(term)[0];
            re = / i($|n\s?)/ig;
            var bef = term.substr(0, term.indexOf(re.exec(term)[0]));
            for (var i =0, len = splitData.length; i < len; i++) {
                var cat = splitData[i][0]
                if (cat === "Courses" || cat === "Professors")
                    continue
                res.push({
                    label: bef+" in ...", 
                    category: "Reviews"
                })
            }
            return {match: match, list: res}
        }
        return null;
    }

    function getTimeList(term) {
        var res = []
        var match;

        var re = /[ap](\.?m\.?|(\s|$))/i;
        var ending;
        if (re.test(term)) {
            ending = re.exec(term)[0];
            var c = ending.charAt(0);
            if (c == 'a' || c == 'A') 
                ending = "am"
            else if (c == 'p' || c == 'P')
                ending = "pm"
        }

        var time
        re = /1[0-2]:?[0-5][0-9]/i;
        if (re.test(term))
            time = re.exec(term)[0];
        else {
            re = /(0?[1-9]|1[0-2]):?([0-5][0-9]?)?/i;
            if (re.test(term))
                time = re.exec(term)[0];
        }
        if (time) {
            time = re.exec(term)[0];
            if (time.charAt(0) == '0')
                time = time.substr(1);
            var cIndex = time.indexOf(":");
            if (cIndex == -1) {
                if (time.length <= 2) 
                    time = time + ":00"
                else {
                    time = time.substr(0,2) + ":" + time.substr(2,4)
                }
            }
            else if (cIndex == time.length-1)
                time = time + "00";
            else if (cIndex == time.length-2)
                time = time + "0"

            if (ending)
                time = time + ending
            else if (time.match(/([89]|1[01]):/i))
                time = time + "am"
            else
                time = time + "pm"
        }
        

        re = /^\s*(at\s)(0?[1-9]|1[0-2]):?([0-5][0-9]?)?\s*([ap]\.?(m\.?)?)?\s*/i;
        if (re.test(term)) {
            match = re.exec(term)[0]
            res.push({label: "at " + time, category: "Time"});
            return {match: match, list: res};
        }

        // should also just have something for aksdjfhk and add in whatever
        re = /^\s*a($|t\s?)/i;
        if (re.test(term)) {
            match = re.exec(term)[0];
            res.push({label: "at 11:00am", category: "Time"});
            res.push({label: "at 1:30pm", category: "Time"});
            return {match: match, list: res};
        }
        return null;
    }

    function getDateList(term) {
        var res = []
        var match;

        var re = /^\s*o($|n\s*)/i;
        if (re.test(term)) {
            match = re.exec(term)[0];
            res.push({label: "on MWF", category: "Days of Week"});
            res.push({label: "on TTh", category: "Days of Week"});
            return {match: match, list: res};
        }

        return null;
    }
    
    if (splitData) {
        $('.autosearch').focus(function() {
            //idk do something
        });

        $(".autosearch").catcomplete({
            delay: 0,
            minlength: 0,
            source: function(request, response) {
                var term = request.term
                var res = []

                if (term.match(/^\s*$/g)) {
                    response(getEmptyList());
                    return
                }
                
                var esc = $.ui.autocomplete.escapeRegex( request.term );
                var matcher = new RegExp(esc.replace(/\\ /g, " .*"), "i");
                for (var i = 0, len = splitData.length; i < len; i++) {
                    var cat = splitData[i][0];
                    for (var j = 1, len2 = splitData[i].length, max=5, count=0; j < len2 && count <= max; j++) {
                        var lab = splitData[i][j];
                        if (matcher.test(lab) == true) {
                            res.push({label: lab, category: cat});
                            count++;
                        }
                    }
                }

                var adv = []
                var search = term
                while (search.length > 0) {
                    console.log("START")
                    console.log("Search: " + search)
                    var r = undefined;
                    var match = undefined;
                    var list = undefined;
                    r = getTimeList(search);
                    if (!r) { // consider doing all of them? or figure out best order
                        r = getDateList(search)
                        if (!r)
                            r = getReviewList(search);
                    }
                    if (r) {
                        console.log("SUCCESS")
                        console.log("Match: " + r.match)
                        search = search.substr(r.match.length)
                        if (adv.length == 0) 
                            adv = r.list;
                        else {
                            temp = []
                            for (var i = 0; i < adv.length; i++) {
                                var old = adv[i]
                                for (var j = 0; j < r.list.length; j++) {
                                    n = r.list[j]
                                    temp.push({
                                        label: old.label + " " + n.label,
                                        category: "Advanced"
                                    });
                                }
                            }
                            adv = temp;
                        }
                    }
                    else {
                        var space = search.indexOf(" ");
                        if (space != -1)
                            search = search.substr(space+1);
                        else
                            break;
                    }
                    console.log("END")
                    console.log("Search: " + search)
                }
                res = res.concat(adv)
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
                    window.location = "http://localhost:8000/courses/" + cnd + cnn
                }
                else if (dmpatt.test(t) == true) {
                    d = dpatt.exec(t)
                    window.location = "http://localhost:8000/depts/" + d
                }
                else if (t.search(/".+" in [a-z]+/i) != -1) {
                    var q = t.match(/".+" in [a-z]+:?/i)[0]
                    if (q.search(/:$/) != -1) {
                        q = q.match(/".+" in [a-z]+/i)[0]
                    }
                    q.replace(/\s/g, "+")
                    window.location = "http://localhost:8000/search/?q=" + q
                } else {
                    p = t.replace(/\s/g, "+")
                    window.location = "http://localhost:8000/search/?q=" + p
                }
            }
        });
    }
});
