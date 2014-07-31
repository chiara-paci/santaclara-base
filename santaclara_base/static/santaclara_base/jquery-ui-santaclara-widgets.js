(function($) {

/**** TreeView ****/

/**** Agisce su tabelle.

Ogni riga della tabella che contiene dati deve avere come classe "sc-tree-data". 
Devono essere definiti:
- data-level: intero che indica il livello di indentazione;
- data-has_children: 0=non può avere righe-figlie,1=può avere righe figlie;
- data-label;
- se data-has_children=1, data-label_children.

Le righe di primo livello devono avere come data-label esattamente options.first_label.
Le righe dei livelli successivi devono avere come data-label il data-label_children della riga parent.
Il data-label_children deve essere formato a partire da data-label aggiungendo un suffisso a piacere.
Il td da usare come campo di riferimento deve avere data-label=options.title_column.

Ad esempio:
<table id="tabid">
<tr class="sc-tree-data" data-level="0" data-has_children="1" data-label="prima" data-label_children="prima-a">
    <td data-label="rif">Riga A</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="0" data-label="prima-a">
    <td data-label="rif">Riga A.1</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="0" data-label="prima-a">
    <td data-label="rif">Riga A.2</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="0" data-has_children="1" data-label="prima" data-label_children="prima-b">
    <td data-label="rif">Riga B</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="0" data-label="prima-b">
    <td data-label="rif">Riga B.1</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="1" data-label="prima-b" data-label_children="prima-b-2">
    <td data-label="rif">Riga B.2</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="0" data-label="prima-b-2">
    <td data-label="rif">Riga B.2.1</td><td>altro</td></tr>
<tr class="sc-tree-data" data-level="1" data-has_children="0" data-label="prima-b-2">
    <td data-label="rif">Riga B.2.2</td><td>altro</td></tr>
</table>

$("#tabid").treeview({title_column: "rif",first_label: "prima"});

****/

    $.widget("sc.sc_treeview", {
	options: {
	    title_column: "title",
	    first_label: "treemodel",
	    indent: 1,
	    row_close: "caret-right",
	    row_open: "caret-down",
	    row_element: "",
	    click_on: null
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    el.addClass("sc-treeview");
	    self.set_logic();
	},
	set_logic: function(){
	    var self=this;
	    var opts=self.options;
	    var el=self.element;
	    el.find("tr.sc-tree-data").each(function(){
		var oldhtml=$(this).html();
		var tdtitle=$(this).children("td[data-label='"+opts.title_column+"']").first();
		var indent=0;
		var prefix="";
		var postfix="";
		if ($(this).data("has_children")) {
		    if (opts.row_close) 
			prefix+="<i class=\"fa fa-"+opts.row_close+"\"></i>&nbsp;";
		}
		else {
		    if (opts.row_element) 
			prefix="<i class=\"fa fa-"+opts.row_element+"\"></i>&nbsp;";
		}
		for(n=0;n<$(this).data("level");n++) indent+=opts.indent;
		tdtitle.css({"text-align":"left","padding-left":indent+"em"});
		tdtitle.html(prefix+tdtitle.html()+postfix);
		if ($(this).data("label")==opts.first_label) 
		    $(this).show();
		else 
		    $(this).hide();
		if (!$(this).data("has_children")) {
		    $(this).click(function(event){
			event.preventDefault();
			opts.click_on(event,$(this));
		    });
		    return
		}
		$(this).data("status","closed");
		$(this).click(function(event){
		    event.preventDefault();
		    var icon=$(this).children().find("i.fa").first();
		    var act_on=$(this).data("label_children");
		    var status=$(this).data("status");
		    if (status=="closed") {
			$("tr[data-label='"+act_on+"']").show();
			$(this).data("status","open");
			icon.removeClass("fa-"+opts.row_close);
			icon.addClass("fa-"+opts.row_open);
		    }
		    else {
			$("tr[data-label^='"+act_on+"']").hide();
			$(this).data("status","closed");
			icon.removeClass("fa-"+opts.row_open);
			icon.addClass("fa-"+opts.row_close);
		    }
		    opts.click_on(event,$(this));
		});
	    });
	},
    }); // sc.sc_treeview

    /***** sc_hpanel ****/

    $.widget("sc.sc_hpanel", {
	options: {
	    right_name: "right",
	    left_name: "left",
	    big: "right",
	    min_height: 400,
	    distance: "1pt",
	    min_width: 85,
	    max_width: 10,
	    start_width: 77,
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";
	    self.right=$("#"+opts.right_name);
	    self.left=$("#"+opts.left_name);
	    el.css({ "position": "relative" });
	    var leftw;
	    var rightw;
	    if (opts.big=="left") {
		leftw=opts.start_width+"%";
		rightw=(opts.min_width+opts.max_width-opts.start_width)+"%";
	    }
	    else {
		rightw=opts.start_width+"%";
		leftw=(opts.min_width+opts.max_width-opts.start_width)+"%";
	    }
	    self.left.css({ "vertical-align": "top",
			    "display": "inline-block",
			    "padding": ".5em",
			    "margin": "0",
			    "width": leftw,
			    "min-width": "10%",
			    "max-width": "85%",
			    "min-height": opts.min_height,
			    "height": opts.min_height
			  });
	    self.right.css({ "margin": "0",
			     "padding": ".5em",
			     "margin-left": opts.distance,
			     "width": rightw, 
			     "min-width": "10%",
			     "max-width": "85%",
			     "display": "inline-block",
			     "vertical-align": "top",
			     "height": opts.min_height,
			     "min-height": opts.min_height
			   });
	    self.rightw=self.right.width();
	    self.left.resizable({ 
		handles: "e, se",
		"start": function( event, ui ) {
		    self.rightw=self.right.width();
		},
		"resize": function( event, ui ) {
		    var diff=ui.size.width-ui.originalSize.width;
		    self.right.height(ui.size.height);
		    self.right.width(self.rightw-diff);
		}   
	    });
	    self.reset_heights();
	},
	reset_heights: function () {
	    this.right.height("auto");
	    this.left.height("auto");
	    var starth=Math.max(this.options.min_height,this.left.height(),this.right.height());
	    //console.log(starth,this.left.height(),this.right.height());
	    //console.log("left",this.left,this.left.outerHeight(),this.left[0].scrollHeight);
	    this.right.height(starth);
	    this.left.height(starth);
	}

    }); // sc.sc_hpanel


    /****/
 
})(jQuery);