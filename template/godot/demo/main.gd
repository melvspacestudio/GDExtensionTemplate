extends Node


func _ready() -> void:
	$Message.text = $Extension.greet()
