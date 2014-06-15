insert into santaclara_base_version (id,label,created_by_id,modified_by_id,created,last_modified,
                                     valid,is_current,text,content_type_id,object_id)
       select 0,'0.0',u.id,u.id,now(),now(),true,false,'(empty)',1,1 
              from auth_user as u order by date_joined limit 1;
