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
	    click_on: null,
	    click_pre: null
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    el.addClass("sc-treeview");
	    self.set_logic();
	},
	set_logic_on_row: function(row){
	    var self=this;
	    var opts=self.options;
	    var oldhtml=row.html();
	    var tdtitle=row.children("td[data-label='"+opts.title_column+"']").first();
	    var indent=0;
	    var prefix="";
	    var postfix="";
	    if (row.data("has_children")) {
		if (opts.row_close) 
		    prefix+="<i class=\"fa fa-"+opts.row_close+"\"></i>&nbsp;";
	    }
	    else {
		if (opts.row_element) 
		    prefix="<i class=\"fa fa-"+opts.row_element+"\"></i>&nbsp;";
	    }
	    for(n=0;n<row.data("level");n++) indent+=opts.indent;
	    tdtitle.css({"text-align":"left","padding-left":indent+"em"});
	    tdtitle.html(prefix+tdtitle.html()+postfix);
	    if (row.data("label")==opts.first_label) 
		row.show();
	    else 
		row.hide();
	    if (!row.data("has_children")) {
		row.click(function(event){
		    event.preventDefault();
		    if (opts.click_pre) opts.click_pre(event,row);
		    if (opts.click_on) opts.click_on(event,row);
		});
		return
	    }
	    row.data("status","closed");
	    row.click(function(event){
		event.preventDefault();
		var icon=row.children().find("i.fa").first();
		var act_on=row.data("label_children");
		var status=row.data("status");
		if (opts.click_pre) opts.click_pre(event,row);
		if (status=="closed") {
		    $("tr[data-label='"+act_on+"']").show();
		    row.data("status","open");
		    icon.removeClass("fa-"+opts.row_close);
		    icon.addClass("fa-"+opts.row_open);
		}
		else {
		    $("tr[data-label^='"+act_on+"']").hide();
		    row.data("status","closed");
		    icon.removeClass("fa-"+opts.row_open);
		    icon.addClass("fa-"+opts.row_close);
		}
		if (opts.click_on) opts.click_on(event,row);
	    });
	},
	set_logic: function(){
	    var self=this;
	    var opts=self.options;
	    var el=self.element;
	    el.find("tr.sc-tree-data").each(function(){
		self.set_logic_on_row($(this));
	    });/* .each(function(){ */
	},
    }); // sc.sc_treeview


    /********************************************************************************************************/

    /***** sc_hpanel ****/
    /**** Agisce su div (di principio).
	  
	  <div id="example">
	  <div id="exampleleft"></div>
	  <div id="exampleright"></div>
	  </div>
	  
	  $("#example").sc_hpanel({
	  right_name: "exampleright",
	  left_name: "exampleleft"
	  });
	  
	  Attenzione che il div "left" deve precedere nel DOM il div "right" o si intorta.
	  
    ****/

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
	    this.right.css({ "min-height": starth });
	    this.left.css({ "min-height": starth });
	}

    }); // sc.sc_hpanel


    /********************************************************************************************************/

    /***** sc_editbox ****/
    /*** Agisce su un div con tre "a" dentro e due aree esterne (uno span/div e una textarea) ed eventualmente
	 un'area da cancellare (tipicamente il parent).
	 
	 <div id="exampleparent">
           <div id="example"
                data-target_view_id="exampletext"
                data-textarea_id="exampletextarea"
                data-deletable="true"
                data-delete_url="/obj/delete/url"
	        data-delete_target_dom_id="exampleparent"
	        data-save_url="/obj/save/url">
	     <a href="" class="santa_clara_edit"><i class="fa fa-edit"></i></a>
	     <a href="" class="santa_clara_delete"><i class="fa fa-trash-o"></i></a>
	     <a href="" class="santa_clara_save"><i class="fa fa-save"></i></a>
           </div>
           <span id="exampletext">text</span>
           <textarea id="exampletextarea">text</textarea>
	 </div>

	 $("#example").sc_editbox({
             save_data_function: function(elem,text){
	         ...
	         return { ... };
	     },
             save_post_function: function(elem,resp){
	         ...
	     }
	 });

    ***/

    $.widget("sc.sc_editbox", {
	options: {
	    edit_class: "santa_clara_edit",
	    delete_class: "santa_clara_delete",
	    save_class: "santa_clara_save",
	    delete_show_always: false,
	    bind_enter: false,
	    delete_dom_function: function(elem,delete_target_dom_id){
		$("#"+delete_target_dom_id).remove();
	    },
	    delete_data_function: function(elem){
		return {};
	    },
	    delete_post_function: function(elem,resp){},
	    save_data_function: function(elem,text){
		return { "text": text };
	    },
	    save_post_function: function(elem,resp){}
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";

	    var target_view_id=el.data("target_view_id");
	    var textarea_id=el.data("textarea_id");
	    var textarea=$("#"+textarea_id);
	    var target_view=$("#"+target_view_id);

	    var edit_buttons=el.find("."+opts.edit_class);
	    var save_buttons=el.find("."+opts.save_class);
	    var delete_buttons=el.find("."+opts.delete_class);

	    textarea.hide();
	    target_view.show();
	    edit_buttons.show();
	    save_buttons.hide();

	    var deletable=false;
	    if ( (el.data("deletable")==true) ||
		 (el.data("deletable")=="true") ||
		 (el.data("deletable")=="yes") )
		deletable=true;

	    if (opts.delete_show_always && deletable) {
		delete_buttons.show();
	    }
	    else {
		delete_buttons.hide();
	    }

	    /** edit **/
	    edit_buttons.click(function(event){
		event.preventDefault();
		var target_view_id=el.data("target_view_id");
		var textarea_id=el.data("textarea_id");
		var textarea=$("#"+textarea_id);
		var target_view=$("#"+target_view_id);
		var edit_buttons=el.find("."+opts.edit_class);
		var save_buttons=el.find("."+opts.save_class);
		var delete_buttons=el.find("."+opts.delete_class);

		var text=target_view.text();
		var deletable=false;
		if ( (el.data("deletable")==true) ||
		     (el.data("deletable")=="true") ||
		     (el.data("deletable")=="yes") )
		    deletable=true;
		textarea.val(text);
		textarea.show();
		target_view.hide();
		edit_buttons.hide();
		save_buttons.show();
		if (deletable)
		    delete_buttons.show();
	    });

	    var save_object=function(){
		var target_view_id=el.data("target_view_id");
		var textarea_id=el.data("textarea_id");
		var textarea=$("#"+textarea_id);
		var target_view=$("#"+target_view_id);
		var edit_buttons=el.find("."+opts.edit_class);
		var save_buttons=el.find("."+opts.save_class);
		var delete_buttons=el.find("."+opts.delete_class);
		var deletable=false;
		if ( (el.data("deletable")==true) ||
		     (el.data("deletable")=="true") ||
		     (el.data("deletable")=="yes") )
		    deletable=true;

		var text=textarea.val();
		var data=opts.save_data_function(el,text);
		var save_url=el.data("save_url");

		$.post(save_url,data)
		    .done( function(resp){
			target_view.text(text);
			opts.save_post_function(el,resp);
			textarea.hide();
			target_view.show();
			edit_buttons.show();
			save_buttons.hide();
			if (opts.delete_show_always && deletable)
			    delete_buttons.show();
			else
			    delete_buttons.hide();
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
	    };

	    /** enter **/

	    if (opts.bind_enter)
		textarea.keyup(function(event){
		    if (event.which!=13) return;
		    event.preventDefault();
		    save_object();
		});

	    /** save **/
	    save_buttons.click(function(event){
		event.preventDefault();
		save_object();
	    });

	    /** delete **/
	    delete_buttons.click(function(event){
		event.preventDefault();

		var deletable=false;
		if ( (el.data("deletable")==true) ||
		     (el.data("deletable")=="true") ||
		     (el.data("deletable")=="yes") )
		    deletable=true;
		if (!deletable) return;

		var delete_target_dom_id=el.data("delete_target_dom_id");
		opts.delete_dom_function(el,delete_target_dom_id);

		var delete_url=el.data("delete_url");
		if (!delete_url) return;

		var data=opts.delete_data_function(el);

		$.post(delete_url,data)
		    .done( function(resp){
			opts.delete_post_function(el,resp);
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
	    });
	    
	}// sc.sc_editbox._create

    }); // sc.sc_editbox

    /***** sc_addform ****/
    /*** Agisce su un "a" e un div correlato contenente il form.
	 
	 <a href="" id="example" class="exampleclass" data-dialog_id="examplebox">Example</a>
	 <div class="form" id="exampleform">
         ...
         <form id="exampleform"> 
         ...
         </form>
         <div class="commands">
         <a href="" class="santa_clara_submit" data-submit_url="/example/url">example</a> 
         <a href="" class="santa_clara_cancel"">cancel</a> 
         </div>
	 </div>

	 $("#example").sc_addform({
	 form_data :function(submit_button,form){
	 ...
	 return { ... };
	 },
	 form_setup: function(elem){
	 ...
	 },
	 form_post: function(resp){
	 ...
	 }
	 });

    ***/

    $.widget("sc.sc_addform", {
	options: {
	    submit_class: "santa_clara_submit",
	    cancel_class: "santa_clara_cancel",
	    form_setup: function(elem){},
	    form_post: function(resp){},
	    form_data: function(submit_button,form){ return {}; }
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";

	    var dialog_id=el.data("dialog_id");
	    var dialog=$("#"+dialog_id);

	    var submit_buttons=dialog.find("."+opts.submit_class);
	    var cancel_buttons=dialog.find("."+opts.cancel_class);

	    dialog.hide();

	    /** el **/
	    el.click(function(event){
		event.preventDefault();
		var dialog_id=el.data("dialog_id");
		var form=$("#"+dialog_id).find("form").first();
		opts.form_setup(el,form);
		$("#"+dialog_id).show();
	    });

	    /** cancel **/
	    cancel_buttons.click(function(event){
		event.preventDefault();
		var dialog_id=el.data("dialog_id");
		$("#"+dialog_id).hide();
	    });

	    /** submit **/
	    submit_buttons.click(function(event){
		event.preventDefault();
		var dialog_id=el.data("dialog_id");
		var submit_url=$(this).data("submit_url");
		var form=$("#"+dialog_id).find("form").first();
		var data=opts.form_data($(this),form);

		$("#"+dialog_id).hide();

		$.post(submit_url,data)
		    .done( function(resp){
			opts.form_post(resp);
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
		
	    });
	    
	}// sc.sc_addform._create

    }); // sc.sc_addform
    /****/
 
})(jQuery);