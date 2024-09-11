<?php
// Start the session at the top
session_start();

if (isset($_GET['logout'])) {    
    // Simple exit message 
    $logout_message = "<div class='msgln'><span class='left-info'>User <b class='user-name-left'>" . $_SESSION['name'] . "</b> has left the chat session.</span><br></div>";
    file_put_contents("log.html", $logout_message, FILE_APPEND | LOCK_EX);
    
    session_destroy();
    header("Location: index.php"); // Redirect the user 
    exit;
}

if (isset($_POST['enter'])) {
    if ($_POST['name'] != "") {
        $_SESSION['name'] = stripslashes(htmlspecialchars($_POST['name']));
        // Debugging message to check if the session is being set
        echo "<p>Session is set with name: " . $_SESSION['name'] . "</p>";
    } else {
        echo '<span class="error">Please type in a name</span>';
    }
}

function loginForm() {
    echo 
    '<div id="loginform"> 
<p>Please enter your name to continue!</p> 
<form action="index.php" method="post"> 
<label for="name">Name &mdash;</label> 
<input type="text" name="name" id="name" /> 
<input type="submit" name="enter" id="enter" value="Enter" /> 
</form> 
</div>';
}
?>

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Connectify Chat Room</title>
        <meta name="description" content="Welcome to Connectify Chat Room" />
        <link rel="stylesheet" href="style.css" />
    </head>
    <body>
    <?php
    // Debugging message to show if the session is working
    if (!isset($_SESSION['name'])) {
        loginForm();
    } else {
        echo "<p>Welcome to the chat room, " . $_SESSION['name'] . "!</p>";
    }
    ?>
    </body>
</html>

