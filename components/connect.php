<?php
   $db_host = "mysql-dev-blog-lananhngo685-dev-blog.h.aivencloud.com";
   $db_username = "avnadmin";
   $db_password = "AVNS_rJlKFXve7NFmsh7WIVB";
   $db_name = "defaultdb";
   $db_port = "14981";

   try {       
      $conn = new PDO("mysql:host=$db_host;port=$db_port;dbname=$db_name", $db_username, $db_password);       
      $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
   }     
   catch(PDOException $e) {       
      echo "Connection failed: " . $e->getMessage();    
   }

?>