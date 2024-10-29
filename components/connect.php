<?php
   $db_host = "bmqecusymwinulglrkb8-mysql.services.clever-cloud.com";
   $db_username = "uxrgdbrv5awov6h8";
   $db_password = "nqHPla81ZThxFdT45y8C";
   $db_name = "bmqecusymwinulglrkb8";

   try {
      $conn = new PDO("mysql:host=$db_host;dbname=$db_name", $db_username, $db_password);
      $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
   }

   catch(PDOException $e) {
      echo "Connection failed: " . $e->getMessage();
   }

?>