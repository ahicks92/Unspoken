import camlorn_audio

camlorn_audio.init_camlorn_audio()

sound = camlorn_audio.Sound3D(filename=r"..\examples\sounds\longtest.wav")
reverb = camlorn_audio.Reverb()

sound.set_effect_for_slot(reverb, 0)

sound.play()