<?xml version="1.0" encoding="utf-8"?>
<Element>
    <Script>
        <Name>BridgeBeam.py</Name>
        <Title>BridgeBeam</Title>
        <Version>1.0</Version>
    </Script>

    <Page>
        <Name>Page3</Name>
        <Text>Polygon3D</Text>

        <Parameter>
            <Name>Color3</Name>
            <Text>Колір</Text>
            <Value>1</Value>
            <ValueType>Color</ValueType>
        </Parameter>

        <Parameter>
            <Name>Separator1</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>BeamLength</Name>
            <Text>Довжина балки</Text>
            <Value>8000.</Value>
            <MinValue>8000.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Separator2</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>TopShWidth</Name>
            <Text>Ширина верхньої полиці</Text>
            <Value>400.</Value>
            <MinValue>400.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>BotShWidth</Name>
            <Text>Ширина нижньої полиці</Text>
            <Value>400.</Value>
            <MinValue>400.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>RibThick</Name>
            <Text>Товщина ребра</Text>
            <Value>160.</Value>
            <MinValue>160.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Separator3</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>BeamHeight</Name>
            <Text>Висота балки</Text>
            <Value>800.</Value>
            <MinValue>800.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>BotShLowHeight</Name>
            <Text>Нижня висота нижньої полиці</Text>
            <Value>150.</Value>
            <MinValue>150.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>BotShUpHeight</Name>
            <Text>Верхня висота нижньої полиці</Text>
            <Value>160.</Value>
            <MinValue>160.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>RibHeight</Name>
            <Text>Висота ребра</Text>
            <Value>450.</Value>
            <MinValue>450.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>TopShHeight</Name>
            <Text>Висота верхньої полиці</Text>
            <Value>300.</Value>
            <MinValue>300.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Separator4</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>HoleDepth</Name>
            <Text>Глибина отвору</Text>
            <Value>350.</Value>
            <MinValue>350.</MinValue>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>HoleHeight</Name>
            <Text>Висота отвору для стропи</Text>
            <Value>540.</Value>
            <ValueType>Length</ValueType>
        </Parameter>

        <Parameter>
            <Name>Separator5</Name>
            <ValueType>Separator</ValueType>
        </Parameter>

        <Parameter>
            <Name>RotationAngleX</Name>
            <Text>Кут повороту по X</Text>
            <Value>0</Value>
            <ValueType>Angle</ValueType>
        </Parameter>

        <Parameter>
            <Name>RotationAngleY</Name>
            <Text>Кут повороту по Y</Text>
            <Value>0</Value>
            <ValueType>Angle</ValueType>
        </Parameter>

        <Parameter>
            <Name>RotationAngleZ</Name>
            <Text>Кут повороту по Z</Text>
            <Value>0</Value>
            <ValueType>Angle</ValueType>
        </Parameter>
    </Page>    
</Element>
