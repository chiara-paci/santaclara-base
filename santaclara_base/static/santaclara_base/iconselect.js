$(document).ready(function(){

    var santa_clara_icon_select=function(obj){
	var value=obj.data("value");
	var target_view=obj.data("target_view");
	var target_input=obj.data("target_input");
	var text=obj.html();
	text+=' <i class="fa fa-caret-down"></i>';

	$("#"+target_input).val(value);
	$("#"+target_view).html(text);

	obj.parent().find("li.selected").removeClass("selected");
	obj.parent().addClass("selected");
	obj.parent().parent().hide();
    };

    $(".santaclaraiconselect").click(function(event){
	event.preventDefault();
	santa_clara_icon_select($(this));
    });

    $(".santaclaraiconselectview").click(function(event){
	event.preventDefault();
	var optionsarea_id=$(this).data("optionsarea_id");
	var target_view=$("#"+optionsarea_id).data("target_view");
	var target_input=$("#"+optionsarea_id).data("target_input");
	var current_val=$("#"+target_input).val();

	if ( $("#"+optionsarea_id).data("filled")=="no" ) {
	    var url="/santaclara_base/json/iconfamily/";
	    $.getJSON( url )
		.done(function(json){
		    var html='',i,j,iconfamily,icon,icon_html;
		    console.log(json);
		    for(i=0;i<json.length;i++){
			iconfamily=json[i];
			html+='<li class="familyname">';
			html+='<a href="" class="santaclarafamilytoggle" data-target_class="iconfamily'+iconfamily["id"]+'">';
			html+=iconfamily["name"];
			html+=' <i class="fa fa-caret-right"></i></a></li>\n';
			for(j=0;j<iconfamily["icon_set"].length;j++){
			    icon=iconfamily["icon_set"][j];
			    icon_html=$('<div/>').html(icon["html"]).text();
			    html+='<li data-value="'+icon["id"]+'"';
			    if (parseInt(icon["id"])==parseInt(current_val))
				html+=' class="selected santaclaraiconli iconfamily'+iconfamily["id"]+'"';
			    else
				html+=' class="santaclaraiconli iconfamily'+iconfamily["id"]+'"';
			    html+='>';
			    html+='<a class="santaclaraiconselect" href=""'
			    html+=' data-value="'+icon["id"]+'"'
			    html+=' data-target_view="'+target_view+'"'
			    html+=' data-target_input="'+target_input+'"'
			    html+='>'+icon_html+'</a></li>\n';
			}			
		    }
		    $("#"+optionsarea_id).html(html);

		    $(".santaclaraiconselect").click(function(event){
			event.preventDefault();
			santa_clara_icon_select($(this));
		    });

		    $(".santaclaraiconli").hide();

		    $(".santaclarafamilytoggle").click(function(event){
			event.preventDefault();
			var target_class=$(this).data("target_class");
			$("."+target_class).toggle();
		    });

		    $("#"+optionsarea_id).data("filled","yes");

		})
		.fail(function(jqxhr,textStatus,error){
		    var err = textStatus + ", " + error;
		    console.log( "Request Failed: " + url );
		    console.log( "Request Failed: " + err );
		});

	}

	$("#"+optionsarea_id).toggle();
    });

    $("ul.santaclaraiconselectul").hide();

/*    $(".taginput").each(function(index){
	var open_tl=$(this).find("a.taglistopen").first();
	var close_tl=$(this).find("a.taglistclose").first();
	var div_tl=$(this).find(".taglist").first();

	open_tl.show();
	close_tl.hide();
	div_tl.hide();
	
	open_tl.click(function(event){
	    close_tl.show();
	    open_tl.hide();
	    div_tl.show();
	});
	
	close_tl.click(function(event){
	    close_tl.hide();
	    open_tl.show();
	    div_tl.hide();
	});
	
	$(".taglabel").click(function(event){
	    var label=$(this).html();
	    var widget_name=$(this).data("widget-name");
	    var entry_tl=$('#id_'+widget_name);
	    entry_tl.val(label);
	});
	
    });

*/

});
