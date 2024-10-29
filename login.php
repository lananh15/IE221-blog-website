<?php

include 'components/connect.php';

session_start();

if(isset($_SESSION['user_id'])){
   $user_id = $_SESSION['user_id'];
}else{
   $user_id = '';
};

if(isset($_POST['submit'])){

   $email = $_POST['email'];
   $email = filter_var($email, FILTER_SANITIZE_STRING);
   $pass = sha1($_POST['pass']);
   $pass = filter_var($pass, FILTER_SANITIZE_STRING);

   $select_user = $conn->prepare("SELECT * FROM `users` WHERE email = ? AND password = ?");
   $select_user->execute([$email, $pass]);
   $row = $select_user->fetch(PDO::FETCH_ASSOC);

   if($select_user->rowCount() > 0){
      $_SESSION['user_id'] = $row['id'];
      header('location:home.php');
   }else{
      $message[] = 'incorrect username or password!';
   }

}

?>

<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Login</title>
   
   <!-- font awesome cdn link  -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
   <link rel="icon" type="image/x-icon" href="uploaded_img/doraemon.webp">
   <!-- custom css file link  -->
   <link rel="stylesheet" href="css/style.css">

</head>
<body>
   
<!-- header section starts  -->
<!-- <?php include 'components/user_header.php'; ?> -->
<!-- header section ends -->

<section class="form-container">

   <form action="" method="post">
      <img src="uploaded_img/doraemon.webp" style="width:17%">
      <div class="divider">
         <span>OR</span>
      </div>

      
      <label class="label-form">Email</label>
      <input type="email" name="email" required class="box" maxlength="50" oninput="this.value = this.value.replace(/\s/g, '')">
      <label class="label-form">Password</label>
      <input type="password" name="pass" required class="box" maxlength="50" oninput="this.value = this.value.replace(/\s/g, '')">
      <input type="submit" value="Login" name="submit" class="btn">
      <p>Don't have an account yet? <a href="register.php">Register</a></p>
   </form>

</section>



<!-- custom js file link  -->
<script src="js/script.js"></script>

</body>
</html>