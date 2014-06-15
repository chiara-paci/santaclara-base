(function ($) {

    $.widget("cdm.base_annotations_box",{
	options: {
	    prefix: "style"
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";
	    $("#"+opts.prefix+"-annotation-template").hide();
	    $("#"+opts.prefix+"-annotation-form-text").santa_clara_editor({ textarea_id:opts.prefix+"-annotation-form-textarea",
									    textarea_name:"text",
									    editor_size: 6
									  });
	    $("#"+opts.prefix+"-annotation-add-button").click(function(event){
		var prefix_id="#"+opts.prefix+"-annotation-";
		var url=$(prefix_id+"form").data("url");
		var data={};
		var ann_container=$("#"+opts.prefix+"-annotation-container");
		event.preventDefault();
		data["content_type"]=$(this).data("content_type");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-textarea").val();
		$.post(url,data)
		    .done( function(obj){
			ann_row=self._load_annotation(obj,ann_container);
			ann_row.show();
			$(prefix_id+"form-textarea").val("");
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });
	},
	_update_annotation: function(ann){
	    var prefix_id="#"+this.options.prefix+"-annotation-";
	    var ann_text;
	    var ann_id=ann.id;
	    ann_text=$("<div/>").html(ann.text).text();
	    $(prefix_id+"text-"+ann.id).html(ann_text);
	    $(prefix_id+"last-modified-container-"+ann.id).show();
	    $(prefix_id+"last-modified-"+ann.id).html(ann.last_modified);
	    $(prefix_id+"last-modified-by-name-"+ann.id).attr("style","color:"+ann.modified_by.color);
	    $(prefix_id+"last-modified-by-name-"+ann.id).html(ann.modified_by.name);
	},
	_load_annotation: function(ann,container){
	    var ann_template=$("#"+this.options.prefix+"-annotation-template");
	    var ann_area=ann_template.clone();
	    var prefix_id="#"+this.options.prefix+"-annotation-";
	    var ann_text;
	    container.append(ann_area);
	    ann_area.find("[id^="+this.options.prefix+"-annotation]").each(function(){
		if (!$(this).attr("id")) return;
		newid=$(this).attr("id")+"-"+ann.id;
		$(this).attr("id",newid);
	    });
	    ann_area.attr("id",ann_template.attr("id").replace("template","annotation-"+ann.id));
	    ann_area.data("ann_id",ann.id);

	    $(prefix_id+"save-button-"+ann.id).data("url",ann.json_update_url)
		.data("content_type_id",ann.content_type_id)
		.data("object_id",ann.object_id);
	    $(prefix_id+"delete-button-"+ann.id).data("url",ann.json_delete_url);
	    $(prefix_id+"delete-button-"+ann.id).data("parent_id",this.options.prefix+"-annotation-annotation-"+ann.id);

	    $(prefix_id+"edit-button-"+ann.id).data("ann_id",ann.id);
	    $(prefix_id+"save-button-"+ann.id).data("ann_id",ann.id);

	    $(prefix_id+"created-"+ann.id).html(ann.created);
	    $(prefix_id+"created-by-avatar-"+ann.id).attr("src",ann.created_by.avatar);
	    $(prefix_id+"created-by-name-"+ann.id).attr("style","color:"+ann.created_by.color);
	    $(prefix_id+"created-by-name-"+ann.id).html(ann.created_by.name);

	    if ( (!ann.last_modified)||(ann.created==ann.last_modified) ){
		$(prefix_id+"last-modified-container-"+ann.id).hide();
	    }
	    else {
		$(prefix_id+"last-modified-container-"+ann.id).show();
		$(prefix_id+"last-modified-"+ann.id).html(ann.last_modified);
		$(prefix_id+"last-modified-by-name-"+ann.id).attr("style","color:"+ann.modified_by.color);
		$(prefix_id+"last-modified-by-name-"+ann.id).html(ann.modified_by.name);
	    }

	    ann_text=$("<div/>").html(ann.text).text();
	    $(prefix_id+"text-"+ann.id).html(ann_text);
	    
	    ann_text=$("<div/>").html(ann.raw_text).text();
	    $(prefix_id+"raw-text-"+ann.id).html(ann_text);
	    $(prefix_id+"raw-text-"+ann.id).santa_clara_editor({ textarea_id:this.options.prefix+"-annotation-form-textarea-"+ann.id,
								 textarea_name:"text",
								 editor_size: 6
							       });
	    $(prefix_id+"delete-button-"+ann.id).click(function(event){
		var url=$(this).data("url");
		var parent_id=$(this).data("parent_id");
		event.preventDefault();
		$.post(url,data={})
		    .done( function(obj){
			$("#"+parent_id).remove();
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });
	    $(prefix_id+"edit-button-"+ann.id).click(function(event){
		event.preventDefault();
		$(prefix_id+"save-button-"+ann.id).show();
		$(prefix_id+"raw-text-"+ann.id).show();
		$(prefix_id+"text-"+ann.id).hide();
		$(this).hide();
	    });
	    var self=this;
	    $(prefix_id+"save-button-"+ann.id).click(function(event){
		var url=$(this).data("url");
		var data={};
		event.preventDefault();
		data["content_type"]=$(this).data("content_type_id");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-textarea-"+ann.id).val();

		$.post(url,data)
		    .done( function(obj){
			self._update_annotation(obj);
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
		$(prefix_id+"edit-button-"+ann.id).show();
		$(prefix_id+"raw-text-"+ann.id).hide();
		$(prefix_id+"text-"+ann.id).show();
		$(this).hide();
	    });
	    $(prefix_id+"edit-button-"+ann.id).show();
	    $(prefix_id+"save-button-"+ann.id).hide();
	    $(prefix_id+"raw-text-"+ann.id).hide();
	    $(prefix_id+"text-"+ann.id).show();
	    return ann_area;
	},
	load_object: function(obj){
	    var prefix_id="#"+this.options.prefix+"-annotation-";
	    var ann_container=$("#"+this.options.prefix+"-annotation-container");
	    var self=this;
	    $(prefix_id+"form-object-id").attr("value",obj.id);
	    $(prefix_id+"form-content-type").attr("value",obj.content_type_id);
	    $(prefix_id+"add-button").data("content_type",obj.content_type_id);
	    $(prefix_id+"add-button").data("object_id",obj.id);

	    this.element.find("div[id^="+this.options.prefix+"-annotation-annotation]").remove();

	    for (i=0;i<obj.annotations.length;i++){
		ann=obj.annotations[i];
		ann_row=this._load_annotation(ann,ann_container);
		ann_row.show();
	    }
	    
	} /* load_object */

    });

})(jQuery);