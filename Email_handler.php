<?php

    $name = $_POST['name'];
    $visitor_email = $_POST['email'];
    $message = $_POST['message'];
    
    
    $email_from = 'tahsin148@outlook.com';

    $email_subject = "New Form Submisssion";

    $email_body = "User Name: $name.\n".
                    "User Email: $visitor_email.\n".
                        "User Message: $message.\n";

    
    $to = "kshifat97@gmail.com";

    $headers = "Form: $email_from \r\n";

    $headers .= "Reply to: $visitor_email \r\n";

    mail($to,$email_subject,$email_body, $headers);

    header("Location: index.html")



?>