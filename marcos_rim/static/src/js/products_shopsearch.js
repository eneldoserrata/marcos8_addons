

if (!sessionStorage["rrtg"]) {
    sessionStorage["rrtg"] = "all";
};
if (!sessionStorage["rrtqw"]) {
    sessionStorage["rrtqw"] = "all";
};
if (!sessionStorage["rrtqh"]) {
    sessionStorage["rrtqh"] = "all";
};
if (!sessionStorage["rrtqr"]) {
    sessionStorage["rrtqr"] = "all";
};
if (!sessionStorage["rrtqty"]) {
    sessionStorage["rrtqty"] = "all";
};
if (!sessionStorage["rrtclasification"]) {
    sessionStorage["rrtclasification"] = "all";
};

if (sessionStorage["rrtg"] != "all") {
    $("#quality-btn-shop-select").val(sessionStorage["rrtg"]);
};

if (sessionStorage["rrtqw"] != "all") {
    $("#ancho-btn-shop-select").val(sessionStorage["rrtqw"]);
};

if (sessionStorage["rrtqh"] != "all") {
    $("#alto-btn-shop-select").val(sessionStorage["rrtqh"]);
};

if (sessionStorage["rrtqr"] != "all") {
    $("#rin-btn-shop-select").val(sessionStorage["rrtqr"]);
};

if (sessionStorage["rrtqty"] != "all") {
    $("#qty-btn-shop-select").val(sessionStorage["rrtqty"]);
};
if (sessionStorage["rrtclasification"] != "all") {
    $("#clasification-btn-shop-select").val(sessionStorage["rrtclasification"]);
};

$("#quality-btn-shop-select").change(function () {
    sessionStorage["rrtg"] =  this.value;
    rrt_search(rrtget_query());
});

$("#ancho-btn-shop-select").change(function () {
    sessionStorage["rrtqw"] = this.value;
    rrt_search(rrtget_query());
});

$("#alto-btn-shop-select").change(function () {
    sessionStorage["rrtqh"] = this.value;
    rrt_search(rrtget_query());
});

$("#rin-btn-shop-select").change(function () {
    sessionStorage["rrtqr"] = this.value;
    rrt_search(rrtget_query());
});

$("#qty-btn-shop-select").change(function () {
    sessionStorage["rrtqty"] = this.value;
    rrt_search(rrtget_query());
});

$("#clasification-btn-shop-select").change(function () {
    sessionStorage["rrtclasification"] = this.value;
    rrt_search(rrtget_query());
});

String.prototype.rrtsearchfotmat = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

rrt_search = function(result){

    $("#wrap > div.container.oe_website_sale > div:nth-child(1) > div > form > div > input").val("");
    $("#wrap > div.container.oe_website_sale > div:nth-child(1) > div > form > div > input").val(result);
    $("#wrap > div.container.oe_website_sale > div:nth-child(1) > div > form > div > span > a").click();
};


rrtget_query = function () {
    var sku = "{0}-{1}-{2}-{3}-{4}-{5}".rrtsearchfotmat(
        sessionStorage["rrtg"],
        sessionStorage["rrtqw"],
        sessionStorage["rrtqh"],
        sessionStorage["rrtqr"],
        sessionStorage["rrtqty"],
        sessionStorage["rrtclasification"]
    );

    return "sku-"+sku;
};

//rrt_search(rrtget_query());

$.each($(".shop-qty"), function(index, value){
    var qty_value = parseInt($(value).text());
    $(value).text(qty_value);
});


